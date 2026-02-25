import pytest
from selenium.webdriver.support import expected_conditions as ec

class TestCartSmoke:
    
    @pytest.mark.smoke
    def test_add_single_item_to_cart(self, user_login, browser):
        ebb = user_login
        ebb.wait.until(ec.url_contains("inventory"))
        ebb.inventory_page.add_to_cart("Sauce Labs Backpack")
        assert ebb.inventory_page.get_cart_badge_count() == 1
        ebb.inventory_page.cart_icon().click()
        ebb.wait.until(ec.url_contains("cart"))
        assert "Sauce Labs Backpack" in ebb.cart_page.get_cart_item_names()

    @pytest.mark.smoke
    def test_add_multiple_items_to_cart(self, user_login, browser):
        ebb = user_login
        ebb.wait.until(ec.url_contains("inventory"))
        ebb.inventory_page.add_to_cart("Sauce Labs Backpack")
        ebb.inventory_page.add_to_cart("Sauce Labs Bike Light")
        assert ebb.inventory_page.get_cart_badge_count() == 2
        ebb.header.cart_icon().click()
        ebb.wait.until(ec.url_contains("cart"))
        cart_items = ebb.cart_page.get_cart_item_names()
        assert "Sauce Labs Backpack" in cart_items
        assert "Sauce Labs Bike Light" in cart_items

    @pytest.mark.smoke
    def test_remove_item_from_cart(self, user_login, browser):
        ebb = user_login
        ebb.wait.until(ec.url_contains("inventory"))
        ebb.inventory_page.add_to_cart("Sauce Labs Backpack")
        ebb.inventory_page.add_to_cart("Sauce Labs Bike Light")
        ebb.inventory_page.cart_icon().click()
        ebb.wait.until(ec.url_contains("cart"))
        ebb.cart_page.remove_item("Sauce Labs Bike Light")
        cart_items = ebb.cart_page.get_cart_item_names()
        assert "Sauce Labs Bike Light" not in cart_items
        assert "Sauce Labs Backpack" in cart_items
        assert ebb.cart_page.get_cart_badge_count() == 1