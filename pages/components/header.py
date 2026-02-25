from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from pages.base_page import BasePage

class HeaderComponent(BasePage):
    MENU_BUTTON = (By.CSS_SELECTOR, "[data-test='open-menu']")
    CART_LINK = (By.CSS_SELECTOR, "[data-test='shopping-cart-link']")
    MENU_INVENTORY_LINK = (By.CSS_SELECTOR, "[data-test='inventory-sidebar-link']")
    MENU_LOGOUT_LINK = (By.CSS_SELECTOR, "[data-test='logout-sidebar-link']")
    MENU_RESET_LINK = (By.CSS_SELECTOR, "[data-test='reset-sidebar-link']")
    CLOSE_MENU_BUTTON = (By.CSS_SELECTOR, "[data-test='close-menu']")
    PAGE_TITLE = (By.CSS_SELECTOR, "[data-test='title']")
    SORT_DROPDOWN = (By.CSS_SELECTOR, "[data-test='product-sort-container']")

    def open_menu(self):
        self.driver.find_element(*self.MENU_BUTTON).click()

    def logout(self):
        self.open_menu()
        self.wait.until(ec.visibility_of_element_located(self.MENU_LOGOUT_LINK))
        self.driver.find_element(*self.MENU_LOGOUT_LINK).click()

    def get_page_title(self):
        return self.driver.find_element(*self.PAGE_TITLE).text

    def sort_products(self, option_value):
        from selenium.webdriver.support.ui import Select
        Select(self.driver.find_element(*self.SORT_DROPDOWN)).select_by_value(option_value)