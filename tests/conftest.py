"""Pytest configuration and fixtures."""

from __future__ import annotations

import asyncio
import os
from collections.abc import AsyncGenerator
from pathlib import Path

import pytest
from playwright.async_api import Browser, BrowserContext, Page, async_playwright

from qa_framework.api.client import APIClient
from qa_framework.config import get_settings
from qa_framework.db.session import DatabaseManager, close_db_manager
from qa_framework.logging import get_logger
from qa_framework.ui.page_factory import PageFactory

logger = get_logger(__name__)


# --- Configuration ---


def pytest_configure(config: pytest.Config) -> None:
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "ui: UI tests (Playwright)")
    config.addinivalue_line("markers", "api: API tests (httpx)")
    config.addinivalue_line("markers", "db: Database tests")
    config.addinivalue_line("markers", "slow: Slow running tests")
    config.addinivalue_line("markers", "flaky: Known flaky tests")
    config.addinivalue_line("markers", "contract: Contract tests")


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    """Auto-mark tests based on location."""
    for item in items:
        if "tests/ui" in str(item.fspath):
            item.add_marker(pytest.mark.ui)
        elif "tests/api" in str(item.fspath):
            item.add_marker(pytest.mark.api)
        elif "tests/contract" in str(item.fspath):
            item.add_marker(pytest.mark.contract)
        elif "tests/db" in str(item.fspath):
            item.add_marker(pytest.mark.db)


# --- Settings ---


@pytest.fixture(scope="session")
def settings():
    """Get settings instance."""
    return get_settings()


# --- Playwright fixtures ---


@pytest.fixture(scope="session")
def playwright_instance():
    """Playwright instance - session scoped but not shared across xdist workers."""
    return async_playwright()


@pytest.fixture
async def playwright(playwright_instance):
    """Playwright context manager."""
    async with playwright_instance as p:
        yield p


@pytest.fixture
async def browser(playwright, settings) -> AsyncGenerator[Browser, None]:
    """Browser instance - function scoped for xdist compatibility."""
    browser = await playwright[settings.browser.name].launch(
        headless=settings.browser.headless,
        slow_mo=settings.browser.slow_mo,
        args=settings.browser.args,
    )
    yield browser
    await browser.close()


@pytest.fixture
async def context(browser, settings) -> AsyncGenerator[BrowserContext, None]:
    """Browser context with configured viewport."""
    context = await browser.new_context(
        viewport={"width": settings.browser.viewport_width, "height": settings.browser.viewport_height},
        locale=settings.browser.locale,
        timezone_id=settings.browser.timezone_id,
        permissions=settings.browser.permissions or None,
    )
    yield context
    await context.close()


@pytest.fixture
async def page(context) -> AsyncGenerator[Page, None]:
    """Page instance."""
    page = await context.new_page()
    yield page
    await page.close()


@pytest.fixture
def page_factory(page) -> PageFactory:
    """Page factory for creating page objects."""
    return PageFactory(page)


# --- API fixtures ---


@pytest.fixture
async def api_client() -> AsyncGenerator[APIClient, None]:
    """API client instance."""
    client = APIClient()
    yield client
    await client.close()


@pytest.fixture
def api_mock(api_client):
    """Respx mock router for API client."""
    return api_client.mock()


# --- Database fixtures ---


@pytest.fixture(scope="session")
def db_manager() -> DatabaseManager:
    """Database manager instance."""
    return DatabaseManager()


@pytest.fixture
async def db_session(db_manager) -> AsyncGenerator:
    """Database session."""
    async with db_manager.session() as session:
        yield session


# --- Test data fixtures ---


@pytest.fixture
def test_user() -> dict:
    """Test user data."""
    return {
        "username": "tomsmith",
        "password": "SuperSecretPassword!",
    }


@pytest.fixture
def invalid_user() -> dict:
    """Invalid user data."""
    return {
        "username": "invalid",
        "password": "wrong",
    }


# --- Artifacts ---


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Capture screenshots on failure for UI tests."""
    outcome = yield
    rep = outcome.get_result()

    if rep.when == "call" and rep.failed:
        if "page" in item.funcargs:
            page = item.funcargs["page"]
            if not page.is_closed():
                try:
                    screenshots_dir = Path("screenshots")
                    screenshots_dir.mkdir(exist_ok=True)
                    screenshot_path = screenshots_dir / f"failure_{item.name}_{os.getpid()}.png"
                    asyncio.run_coroutine_threadsafe(
                        page.screenshot(path=str(screenshot_path), full_page=True),
                        asyncio.get_event_loop(),
                    ).result(timeout=5)
                except Exception:
                    pass  # Ignore screenshot failures


# --- Cleanup ---


@pytest.fixture(autouse=True, scope="session")
async def cleanup():
    """Session cleanup."""
    yield
    await close_db_manager()


