from pages.page_manager import PageManager

class MobilePageManager(PageManager):
    def __init__(self, driver):
        super().__init__(driver)
        # Currently inherits all web page objects since Sauce Demo 
        # renders consistently across viewports.
        # Mobile-specific page objects will be added here as behavioral differences emerge.