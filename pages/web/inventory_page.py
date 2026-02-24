from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from pages.components.header import HeaderComponent

class InventoryPage(HeaderComponent):
    INVENTORY_LIST = (By.CSS_SELECTOR, "[data-test='inventory-list']")
    INVENTORY_ITEMS = (By.CSS_SELECTOR, "[data-test='inventory-item']")
    ITEM_NAMES = (By.CSS_SELECTOR, "[data-test='inventory-item-name']")
    ITEM_PRICES = (By.CSS_SELECTOR, "[data-test='inventory-item-price']")

    @staticmethod
    def add_to_cart_locator(item_name):
        slug = item_name.lower().replace(" ", "-").replace("(", "").replace(")", "").replace(".", "")
        return By.CSS_SELECTOR, f"[data-test='add-to-cart-{slug}']"

    def add_to_cart(self, item_name):
        locator = self.add_to_cart_locator(item_name)
        self.wait.until(ec.element_to_be_clickable(locator))
        self.driver.find_element(*locator).click()

    def get_inventory_items(self):
        return self.driver.find_elements(*self.INVENTORY_ITEMS)

    def get_item_names(self):
        return [el.text for el in self.driver.find_elements(*self.ITEM_NAMES)]

    def get_item_prices(self):
        return [el.text for el in self.driver.find_elements(*self.ITEM_PRICES)]