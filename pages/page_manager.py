from selenium.webdriver.support.wait import WebDriverWait
from pages.web.login_page import LoginPage
from pages.web.inventory_page import InventoryPage
from pages.web.cart_page import CartPage

class PageManager:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10) # handles most standard wait scenarios
        
        # Sauce Demo pages
        self.login_page = LoginPage(driver)
        self.inventory_page = InventoryPage(driver)
        self.cart_page = CartPage(driver)