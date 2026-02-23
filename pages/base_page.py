from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.wait import WebDriverWait

class BasePage:
    def __init__(self, driver: WebDriver):
        super().__init__()
        if not isinstance(driver, WebDriver):
            raise TypeError("driver must be an instance of selenium.webdriver.remote.webdriver.WebDriver")
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)
        self.timeout = 10