"""Login page object for demo testing."""

from playwright.async_api import Locator

from ..base_page import BasePage


class LoginPage(BasePage):
    """Login page for the-internet.herokuapp.com."""

    url_path = "/login"
    page_title = "The Internet"

    # Locators
    @property
    def username_input(self) -> Locator:
        return self.get_by_label("Username")

    @property
    def password_input(self) -> Locator:
        return self.get_by_label("Password")

    @property
    def login_button(self) -> Locator:
        return self.get_by_role("button", name="Login")

    @property
    def flash_message(self) -> Locator:
        # The flash message has id="flash" but not test_id
        return self.page.locator("#flash")

    @property
    def logout_button(self) -> Locator:
        # It's actually a link, not a button
        return self.get_by_role("link", name="Logout")

    # Actions
    async def login(self, username: str, password: str) -> "LoginPage":
        """Perform login."""
        await self.fill(self.username_input, username)
        await self.fill(self.password_input, password)
        await self.click(self.login_button)
        await self.wait_for_load()
        return self

    async def logout(self) -> "LoginPage":
        """Perform logout."""
        await self.click(self.logout_button)
        await self.wait_for_load()
        return self

    # Assertions
    async def assert_login_success(self) -> "LoginPage":
        """Assert successful login."""
        await self.expect_contains_text(self.flash_message, "You logged into a secure area!")
        await self.expect_visible(self.logout_button)
        return self

    async def assert_login_failure(self, message: str | None = None) -> "LoginPage":
        """Assert failed login."""
        await self.expect_visible(self.flash_message)
        if message:
            await self.expect_contains_text(self.flash_message, message)
        return self

    async def assert_logged_out(self) -> "LoginPage":
        """Assert successful logout."""
        await self.expect_contains_text(self.flash_message, "You logged out of the secure area!")
        await self.expect_visible(self.login_button)
        return self
