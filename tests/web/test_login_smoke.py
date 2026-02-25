import pytest
from selenium.webdriver.support import expected_conditions as ec

class TestLoginSmoke:

    @pytest.mark.smoke
    def test_successful_login(self, user_login, browser):
        ebb = user_login
        assert "inventory" in browser.current_url, "Login did not reach inventory page"
        assert ebb.inventory_page.get_page_title() == "Products", "Inventory page title not found"

    @pytest.mark.smoke
    def test_locked_out_user(self, browser, page_manager):
        from config.settings import SauceConfig
        ebb = page_manager
        browser.get(SauceConfig().base_url)
        ebb.login_page.login(
            username=SauceConfig.USERS["locked_out"]["username"],
            password=SauceConfig.USERS["locked_out"]["password"]
        )
        error = ebb.login_page.get_error_message()
        assert "locked out" in error.lower(), f"Unexpected error message: {error}"

    @pytest.mark.smoke
    def test_invalid_credentials(self, browser, page_manager):
        from config.settings import SauceConfig
        ebb = page_manager
        browser.get(SauceConfig().base_url)
        ebb.login_page.login(username="bad_user", password="bad_pass")
        error = ebb.login_page.get_error_message()
        assert "Username and password do not match" in error, f"Unexpected error message: {error}"