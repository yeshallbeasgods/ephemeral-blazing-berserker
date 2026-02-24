from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from pages.components.header import HeaderComponent

class CartPage(HeaderComponent):
    CART_LIST = (By.CSS_SELECTOR, "[data-test='cart-list']")
    CART_ITEMS = (By.CSS_SELECTOR, "[data-test='inventory-item']")
    ITEM_NAMES = (By.CSS_SELECTOR, "[data-test='inventory-item-name']")
    ITEM_PRICES = (By.CSS_SELECTOR, "[data-test='inventory-item-price']")
    ITEM_QUANTITIES = (By.CSS_SELECTOR, "[data-test='item-quantity']")
    CONTINUE_SHOPPING_BUTTON = (By.CSS_SELECTOR, "[data-test='continue-shopping']")
    CHECKOUT_BUTTON = (By.CSS_SELECTOR, "[data-test='checkout']")
    CART_BADGE = (By.CSS_SELECTOR, "[data-test='shopping-cart-badge']")

    @staticmethod
    def _slug(item_name):
        return item_name.lower().replace(" ", "-").replace("(", "").replace(")", "").replace(".", "")

    @staticmethod
    def remove_button_locator(item_name):
        slug = CartPage._slug(item_name)
        return By.CSS_SELECTOR, f"[data-test='remove-{slug}']"

    def remove_item(self, item_name):
        locator = self.remove_button_locator(item_name)
        self.wait.until(ec.element_to_be_clickable(locator))
        self.driver.find_element(*locator).click()

    def get_cart_item_names(self):
        return [el.text for el in self.driver.find_elements(*self.ITEM_NAMES)]

    def get_cart_item_count(self):
        return len(self.driver.find_elements(*self.CART_ITEMS))

    def get_cart_badge_count(self):
        try:
            return int(self.driver.find_element(*self.CART_BADGE).text)
        except:
            return 0

    def click_checkout(self):
        self.driver.find_element(*self.CHECKOUT_BUTTON).click()

    def click_continue_shopping(self):
        self.driver.find_element(*self.CONTINUE_SHOPPING_BUTTON).click()