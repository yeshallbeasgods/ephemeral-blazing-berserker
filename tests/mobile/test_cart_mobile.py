import pytest
from pages.page_manager import PageManager
from utils.wait_utils import WaitUtils as wu

class TestCartMobile:
    @pytest.mark.mobile
    @pytest.mark.smoke
    def test_add_single_item_to_cart(self, mobile_login, browser):
        ebb: PageManager = mobile_login
        wu.wait_for_url_to_contain(browser, "inventory")
        ebb.inventory_page.add_to_cart("Sauce Labs Backpack")
        ebb.inventory_page.wait_for_cart_count(1)
        ebb.inventory_page.cart_icon().click()
        wu.wait_for_url_to_contain(browser, "cart")
        assert "Sauce Labs Backpack" in ebb.cart_page.get_cart_item_names()

    @pytest.mark.mobile
    @pytest.mark.smoke
    def test_add_multiple_items_to_cart(self, mobile_login, browser):
        ebb: PageManager = mobile_login
        wu.wait_for_url_to_contain(browser, "inventory")
        ebb.inventory_page.add_to_cart("Sauce Labs Backpack")
        ebb.inventory_page.add_to_cart("Sauce Labs Bike Light")
        ebb.inventory_page.wait_for_cart_count(2)
        ebb.inventory_page.cart_icon().click()
        wu.wait_for_url_to_contain(browser, "cart")
        cart_items = ebb.cart_page.get_cart_item_names()
        assert "Sauce Labs Backpack" in cart_items
        assert "Sauce Labs Bike Light" in cart_items
