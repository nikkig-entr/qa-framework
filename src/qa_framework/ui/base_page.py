"""Base Page Object with common interactions and assertions."""

from __future__ import annotations

import time
from abc import ABC
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal

from playwright.async_api import (
    BrowserContext,
    ElementHandle,
    FrameLocator,
    Locator,
    Page,
    TimeoutError as PlaywrightTimeoutError,
    expect,
)
from tenacity import retry, stop_after_attempt, wait_exponential

from ..config import get_settings
from ..logging import get_logger, LogContext

if TYPE_CHECKING:
    from .page_factory import PageFactory

logger = get_logger(__name__)


class BasePage(ABC):
    """Base Page Object with common functionality."""

    url_path: str = ""
    page_title: str | None = None

    def __init__(self, page: Page, page_factory: "PageFactory | None" = None) -> None:
        self.page = page
        self.page_factory = page_factory
        self._settings = get_settings()
        self._log = logger.bind(page=self.__class__.__name__)

    @property
    def base_url(self) -> str:
        return self._settings.ui.base_url.rstrip("/")

    @property
    def full_url(self) -> str:
        base = self.base_url.rstrip("/")
        path = self.url_path.lstrip("/")
        return f"{base}/{path}" if path else base

    async def navigate(self, wait_until: Literal["load", "domcontentloaded", "networkidle"] = "networkidle") -> None:
        """Navigate to page URL."""
        with LogContext(url=self.full_url):
            self._log.info("Navigating to page")
            await self.page.goto(self.full_url, wait_until=wait_until)
            await self.wait_for_load()

    async def wait_for_load(self, timeout: int | None = None) -> None:
        """Wait for page to be fully loaded."""
        timeout = timeout or 30_000
        try:
            await self.page.wait_for_load_state("networkidle", timeout=timeout)
        except PlaywrightTimeoutError:
            self._log.warning("Network idle timeout, continuing anyway")

    async def wait_for_url(self, url_pattern: str, timeout: int | None = None) -> None:
        """Wait for URL to match pattern."""
        await self.page.wait_for_url(url_pattern, timeout=timeout or 10_000)

    # --- Element interactions ---

    def locator(self, selector: str, **kwargs: Any) -> Locator:
        """Create a locator with default options."""
        return self.page.locator(selector, **kwargs)

    def get_by_role(self, role: str, **kwargs: Any) -> Locator:
        return self.page.get_by_role(role, **kwargs)

    def get_by_text(self, text: str, **kwargs: Any) -> Locator:
        return self.page.get_by_text(text, **kwargs)

    def get_by_label(self, label: str, **kwargs: Any) -> Locator:
        return self.page.get_by_label(label, **kwargs)

    def get_by_placeholder(self, placeholder: str, **kwargs: Any) -> Locator:
        return self.page.get_by_placeholder(placeholder, **kwargs)

    def get_by_test_id(self, test_id: str, **kwargs: Any) -> Locator:
        return self.page.get_by_test_id(test_id, **kwargs)

    def frame_locator(self, selector: str) -> FrameLocator:
        return self.page.frame_locator(selector)

    @retry(wait=wait_exponential(multiplier=0.1, min=0.1, max=1), stop=stop_after_attempt(3))
    async def click(self, locator: Locator | str, **kwargs: Any) -> None:
        """Click element with retry."""
        loc = self.locator(locator) if isinstance(locator, str) else locator
        await loc.click(**kwargs)

    @retry(wait=wait_exponential(multiplier=0.1, min=0.1, max=1), stop=stop_after_attempt(3))
    async def fill(self, locator: Locator | str, value: str, **kwargs: Any) -> None:
        """Fill input with retry."""
        loc = self.locator(locator) if isinstance(locator, str) else locator
        await loc.fill(value, **kwargs)

    async def type_text(self, locator: Locator | str, text: str, delay: int = 50) -> None:
        """Type text with delay (simulates human typing)."""
        loc = self.locator(locator) if isinstance(locator, str) else locator
        await loc.type(text, delay=delay)

    async def press(self, locator: Locator | str, key: str, **kwargs: Any) -> None:
        """Press key on element."""
        loc = self.locator(locator) if isinstance(locator, str) else locator
        await loc.press(key, **kwargs)

    async def hover(self, locator: Locator | str, **kwargs: Any) -> None:
        """Hover over element."""
        loc = self.locator(locator) if isinstance(locator, str) else locator
        await loc.hover(**kwargs)

    async def select_option(self, locator: Locator | str, value: str | list[str], **kwargs: Any) -> None:
        """Select option(s) from dropdown."""
        loc = self.locator(locator) if isinstance(locator, str) else locator
        await loc.select_option(value, **kwargs)

    async def check(self, locator: Locator | str, **kwargs: Any) -> None:
        """Check checkbox/radio."""
        loc = self.locator(locator) if isinstance(locator, str) else locator
        await loc.check(**kwargs)

    async def uncheck(self, locator: Locator | str, **kwargs: Any) -> None:
        """Uncheck checkbox."""
        loc = self.locator(locator) if isinstance(locator, str) else locator
        await loc.uncheck(**kwargs)

    # --- Assertions ---

    async def expect_visible(self, locator: Locator | str, timeout: int = 5_000) -> Locator:
        """Assert element is visible."""
        loc = self.locator(locator) if isinstance(locator, str) else locator
        await expect(loc).to_be_visible(timeout=timeout)
        return loc

    async def expect_hidden(self, locator: Locator | str, timeout: int = 5_000) -> Locator:
        """Assert element is hidden."""
        loc = self.locator(locator) if isinstance(locator, str) else locator
        await expect(loc).to_be_hidden(timeout=timeout)
        return loc

    async def expect_enabled(self, locator: Locator | str, timeout: int = 5_000) -> Locator:
        """Assert element is enabled."""
        loc = self.locator(locator) if isinstance(locator, str) else locator
        await expect(loc).to_be_enabled(timeout=timeout)
        return loc

    async def expect_disabled(self, locator: Locator | str, timeout: int = 5_000) -> Locator:
        """Assert element is disabled."""
        loc = self.locator(locator) if isinstance(locator, str) else locator
        await expect(loc).to_be_disabled(timeout=timeout)
        return loc

    async def expect_text(self, locator: Locator | str, text: str, timeout: int = 5_000) -> Locator:
        """Assert element has text."""
        loc = self.locator(locator) if isinstance(locator, str) else locator
        await expect(loc).to_have_text(text, timeout=timeout)
        return loc

    async def expect_contains_text(self, locator: Locator | str, text: str, timeout: int = 5_000) -> Locator:
        """Assert element contains text."""
        loc = self.locator(locator) if isinstance(locator, str) else locator
        await expect(loc).to_contain_text(text, timeout=timeout)
        return loc

    async def expect_value(self, locator: Locator | str, value: str, timeout: int = 5_000) -> Locator:
        """Assert input has value."""
        loc = self.locator(locator) if isinstance(locator, str) else locator
        await expect(loc).to_have_value(value, timeout=timeout)
        return loc

    async def expect_attribute(self, locator: Locator | str, name: str, value: str, timeout: int = 5_000) -> Locator:
        """Assert element has attribute."""
        loc = self.locator(locator) if isinstance(locator, str) else locator
        await expect(loc).to_have_attribute(name, value, timeout=timeout)
        return loc

    async def expect_count(self, locator: Locator | str, count: int, timeout: int = 5_000) -> Locator:
        """Assert element count."""
        loc = self.locator(locator) if isinstance(locator, str) else locator
        await expect(loc).to_have_count(count, timeout=timeout)
        return loc

    async def expect_url(self, pattern: str, timeout: int = 5_000) -> None:
        """Assert current URL matches pattern."""
        await expect(self.page).to_have_url(pattern, timeout=timeout)

    async def expect_title(self, title: str | list[str], timeout: int = 5_000) -> None:
        """Assert page title."""
        await expect(self.page).to_have_title(title, timeout=timeout)

    # --- Screenshots & artifacts ---

    async def screenshot(self, name: str | None = None, full_page: bool = True) -> bytes:
        """Take screenshot and return bytes."""
        name = name or f"{self.__class__.__name__}_{int(time.time())}"
        path = Path(f"screenshots/{name}.png")
        path.parent.mkdir(parents=True, exist_ok=True)
        screenshot_bytes = await self.page.screenshot(path=str(path), full_page=full_page)
        self._log.info("Screenshot taken", path=str(path))
        return screenshot_bytes

    async def screenshot_on_failure(self, test_name: str) -> None:
        """Take screenshot on test failure if enabled."""
        if self._settings.test.screenshot_on_failure:
            await self.screenshot(f"failure_{test_name}")

    # --- Navigation helpers ---

    async def go_back(self) -> None:
        await self.page.go_back()
        await self.wait_for_load()

    async def go_forward(self) -> None:
        await self.page.go_forward()
        await self.wait_for_load()

    async def reload(self) -> None:
        await self.page.reload()
        await self.wait_for_load()

    # --- Wait helpers ---

    async def wait_for_selector(self, selector: str, state: Literal["attached", "detached", "visible", "hidden"] = "visible", timeout: int = 30_000) -> Locator:
        """Wait for selector to reach state."""
        loc = self.page.locator(selector)
        await loc.wait_for(state=state, timeout=timeout)
        return loc

    async def wait_for_function(self, expression: str, timeout: int = 30_000) -> Any:
        """Wait for JavaScript expression to return truthy."""
        return await self.page.wait_for_function(expression, timeout=timeout)

    async def wait_for_response(self, url_pattern: str, timeout: int = 30_000):
        """Wait for network response matching pattern."""
        async with self.page.expect_response(url_pattern) as response_info:
            response = await response_info.value
        return response

    # --- JavaScript execution ---

    async def eval_on_selector(self, selector: str, expression: str, arg: Any = None) -> Any:
        """Evaluate JavaScript on element."""
        return await self.page.locator(selector).evaluate(expression, arg)

    async def eval(self, expression: str, arg: Any = None) -> Any:
        """Evaluate JavaScript in page context."""
        return await self.page.evaluate(expression, arg)

    # --- Cookie / Storage ---

    async def get_cookies(self) -> list[dict]:
        return await self.page.context.cookies()

    async def set_cookies(self, cookies: list[dict]) -> None:
        await self.page.context.add_cookies(cookies)

    async def clear_cookies(self) -> None:
        await self.page.context.clear_cookies()

    async def get_local_storage(self) -> dict:
        return await self.page.evaluate("() => Object.assign({}, localStorage)")

    async def set_local_storage(self, data: dict) -> None:
        await self.page.evaluate("(data) => Object.assign(localStorage, data)", data)

    # --- Page Factory integration ---

    def get_page(self, page_class: type["BasePage"]) -> "BasePage":
        """Get another page instance via factory."""
        if self.page_factory:
            return self.page_factory.get(page_class)
        raise RuntimeError("PageFactory not available")