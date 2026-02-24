from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from pages.base_page import BasePage

class LoginPage(BasePage):
    # Locators
    USERNAME_INPUT = (By.CSS_SELECTOR, "[data-test='username']")
    PASSWORD_INPUT = (By.CSS_SELECTOR, "[data-test='password']")
    LOGIN_BUTTON = (By.CSS_SELECTOR, "[data-test='login-button']")
    ERROR_MESSAGE = (By.CSS_SELECTOR, ".error-message-container")

    def login(self, username, password):
        self.wait.until(ec.visibility_of_element_located(self.USERNAME_INPUT))
        self.driver.find_element(*self.USERNAME_INPUT).send_keys(username)
        self.driver.find_element(*self.PASSWORD_INPUT).send_keys(password)
        self.driver.find_element(*self.LOGIN_BUTTON).click()

    def get_error_message(self):
        return self.wait.until(ec.visibility_of_element_located(self.ERROR_MESSAGE)).text