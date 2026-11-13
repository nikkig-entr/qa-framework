"""Login page UI tests."""

import pytest

from qa_framework.ui.pages import LoginPage


@pytest.mark.ui
class TestLoginPage:
    """Tests for the login page."""

    async def test_page_loads(self, page, page_factory):
        """Test that login page loads."""
        login_page = page_factory.get(LoginPage)
        await login_page.navigate()
        await login_page.expect_visible(login_page.username_input)
        await login_page.expect_visible(login_page.password_input)
        await login_page.expect_visible(login_page.login_button)

    async def test_successful_login(self, page, page_factory, test_user):
        """Test successful login with valid credentials."""
        login_page = page_factory.get(LoginPage)
        await login_page.navigate()
        await login_page.login(test_user["username"], test_user["password"])
        await login_page.assert_login_success()

    async def test_failed_login(self, page, page_factory, invalid_user):
        """Test failed login with invalid credentials."""
        login_page = page_factory.get(LoginPage)
        await login_page.navigate()
        await login_page.login(invalid_user["username"], invalid_user["password"])
        await login_page.assert_login_failure("Your username is invalid!")

    async def test_logout(self, page, page_factory, test_user):
        """Test logout after successful login."""
        login_page = page_factory.get(LoginPage)
        await login_page.navigate()
        await login_page.login(test_user["username"], test_user["password"])
        await login_page.assert_login_success()
        await login_page.logout()
        await login_page.assert_logged_out()

    @pytest.mark.parametrize(("username", "password", "expected_message"), [
        ("", "SuperSecretPassword!", "Your username is invalid!"),
        ("tomsmith", "", "Your password is invalid!"),
        ("", "", "Your username is invalid!"),
    ])
    async def test_empty_credentials(self, page, page_factory, username, password, expected_message):
        """Test login with empty credentials."""
        login_page = page_factory.get(LoginPage)
        await login_page.navigate()
        await login_page.login(username, password)
        await login_page.assert_login_failure(expected_message)


