"""Page Factory for managing Page Object instances."""

from __future__ import annotations

from typing import TYPE_CHECKING

from playwright.async_api import Page

from .base_page import BasePage

if TYPE_CHECKING:
    from ..config import Settings


class PageFactory:
    """Factory for creating and caching Page Object instances."""

    def __init__(self, page: Page, settings: Settings | None = None) -> None:
        self._page = page
        self._settings = settings
        self._cache: dict[type[BasePage], BasePage] = {}

    def get(self, page_class: type[BasePage]) -> BasePage:
        """Get or create a page instance."""
        if page_class not in self._cache:
            self._cache[page_class] = page_class(self._page, self)
        return self._cache[page_class]

    def invalidate(self, page_class: type[BasePage]) -> None:
        """Remove a page from cache."""
        self._cache.pop(page_class, None)

    def clear(self) -> None:
        """Clear all cached pages."""
        self._cache.clear()

    @property
    def page(self) -> Page:
        return self._page

    @property
    def settings(self) -> Settings | None:
        return self._settings
