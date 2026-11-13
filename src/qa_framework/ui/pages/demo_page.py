"""Demo page object for various UI elements testing."""

from playwright.async_api import Locator

from ..base_page import BasePage


class DemoPage(BasePage):
    """Demo page with various UI elements for testing."""

    url_path = "/"
    page_title = "The Internet"

    # Locators
    @property
    def header(self) -> Locator:
        return self.get_by_role("heading", level=1)

    @property
    def subheader(self) -> Locator:
        return self.get_by_role("heading", level=2)

    @property
    def available_examples(self) -> Locator:
        return self.get_by_role("list").get_by_role("listitem")

    @property
    def footer_link(self) -> Locator:
        return self.get_by_role("link", name="Elemental Selenium")

    # Actions
    async def click_example(self, example_name: str) -> None:
        """Click on an example link."""
        link = self.get_by_role("link", name=example_name)
        await self.click(link)
        await self.wait_for_load()

    # Assertions
    async def assert_loaded(self) -> "DemoPage":
        """Assert page is loaded."""
        await self.expect_visible(self.header)
        await self.expect_text(self.header, "Welcome to the-internet")
        await self.expect_visible(self.subheader)
        await self.expect_text(self.subheader, "Available Examples")
        return self

    async def assert_examples_count(self, min_count: int = 70) -> "DemoPage":
        """Assert minimum number of available examples."""
        count = await self.available_examples.count()
        assert count >= min_count, f"Expected at least {min_count} examples, got {count}"
        return self


