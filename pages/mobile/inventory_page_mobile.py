from pages.web.inventory_page import InventoryPage
from utils.browser_utils import BrowserUtils

class MobileInventoryPage(InventoryPage):
    def add_to_cart(self, item_name):
        locator = self.add_to_cart_locator(item_name)
        BrowserUtils.mobile_click(self.driver, locator)
