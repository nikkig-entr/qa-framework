"""Demo page UI tests."""

import pytest

from qa_framework.ui.pages import DemoPage


@pytest.mark.ui
class TestDemoPage:
    """Tests for the demo page."""

    async def test_page_loads(self, page, page_factory):
        """Test that demo page loads correctly."""
        demo_page = page_factory.get(DemoPage)
        await demo_page.navigate()
        await demo_page.assert_loaded()

    async def test_examples_list(self, page, page_factory):
        """Test that examples are listed."""
        demo_page = page_factory.get(DemoPage)
        await demo_page.navigate()
        await demo_page.assert_examples_count(70)  # the-internet has 76+ examples

    async def test_navigation_to_login(self, page, page_factory):
        """Test navigation to login page."""
        demo_page = page_factory.get(DemoPage)
        await demo_page.navigate()
        await demo_page.click_example("Form Authentication")
        # URL should change to /login
        await page.wait_for_url("**/login")

    async def test_footer_link(self, page, page_factory):
        """Test footer link exists."""
        demo_page = page_factory.get(DemoPage)
        await demo_page.navigate()
        await demo_page.expect_visible(demo_page.footer_link)
        await demo_page.expect_attribute(demo_page.footer_link, "href", "https://elementalselenium.com/")


