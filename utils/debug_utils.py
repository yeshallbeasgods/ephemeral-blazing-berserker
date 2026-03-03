from datetime import datetime
from typing import List, Dict

class DebugUtils:
    @staticmethod
    def set_and_print_variable(name, value):
        print(f"{name}: {value}")
        return value

    @staticmethod
    def print_window_handles(driver):
        print("Window Handles:", driver.window_handles)
        print("Total Window Handles:", len(driver.window_handles))
        print("Current Window URL:", driver.current_url)

    @staticmethod
    def print_element_details(element):
        print("Tag Name:", element.tag_name)
        print("Attributes:", element.get_attribute("outerHTML"))
        print("Is Displayed:", element.is_displayed())
        print("Text Content:", element.text)
        print("Coordinates:", element.location)

    @staticmethod
    def print_console_logs(driver):
        # Requires Chrome launched with logging_prefs capability enabled
        logs = driver.get_log("browser")
        for log in logs:
            print(log)

    @staticmethod
    def check_javascript_errors(driver) -> List[Dict]:
        # Useful for catching client-side errors and security-related console violations
        # Returns SEVERE level browser logs; empty list means no errors detected
        logs = driver.get_log("browser")
        errors = [log for log in logs if log["level"] == "SEVERE"]
        return errors

    @staticmethod
    def print_network_requests(driver):
        logs = driver.get_log("performance")
        for log in logs:
            print(log)

    @staticmethod
    def take_screenshot(driver, filename="screenshot", path="reports/screenshots"):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        driver.save_screenshot(f"{path}/{filename}_{timestamp}.png")

    @staticmethod
    def save_page_source(driver, filename="page_source", path="reports/screenshots"):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = f"{path}/{filename}_{timestamp}.html"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(driver.page_source)

    @staticmethod
    def capture_page_state(driver, filename="debug", path="reports/screenshots"):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        driver.save_screenshot(f"{path}/{filename}_{timestamp}.png")
        with open(f"{path}/{filename}_{timestamp}.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)

    # Utilities for helping coding agents debug failing CI tests
    @staticmethod
    def get_page_html(driver) -> str:
        # Returns full page source - useful for agents to inspect current DOM state
        return driver.page_source

    @staticmethod
    def get_element_html(driver, locator) -> str:
        # Returns outer HTML of a specific element - useful for verifying locators
        try:
            element = driver.find_element(*locator)
            return element.get_attribute("outerHTML")
        except Exception as e:
            return f"Element not found: {e}"

    @staticmethod
    def find_elements_by_text(driver, text) -> list:
        # Finds all elements containing specific text - useful for locator discovery
        elements = driver.find_elements("xpath", f"//*[contains(text(), '{text}')]")
        return [el.get_attribute("outerHTML") for el in elements]

    @staticmethod
    def get_all_data_test_attributes(driver) -> list:
        # Returns all data-test attributes on the page - maps available test hooks
        return driver.execute_script("""
            return Array.from(document.querySelectorAll('[data-test]'))
                .map(el => ({
                    tag: el.tagName,
                    dataTest: el.getAttribute('data-test'),
                    text: el.innerText.trim().substring(0, 50),
                    visible: el.offsetParent !== null
                }));
        """)

    @staticmethod
    def get_interactive_elements(driver) -> list:
        # Returns all clickable/interactive elements - helps agents find valid targets
        return driver.execute_script("""
            return Array.from(document.querySelectorAll(
                'button, a, input, select, textarea, [role="button"], [onclick]'
            )).map(el => ({
                tag: el.tagName,
                id: el.id,
                name: el.name || '',
                type: el.type || '',
                text: el.innerText.trim().substring(0, 50),
                visible: el.offsetParent !== null,
                disabled: el.disabled || false
            }));
        """)

    @staticmethod
    def get_element_locator_suggestions(driver, partial_text) -> dict:
        # Given partial text, suggests possible locators - helps agents fix broken selectors
        results = driver.execute_script(f"""
            const text = '{partial_text}'.toLowerCase();
            const elements = Array.from(document.querySelectorAll('*'))
                .filter(el => el.innerText && el.innerText.toLowerCase().includes(text));
            return elements.map(el => ({{
                tag: el.tagName,
                id: el.id || null,
                dataTest: el.getAttribute('data-test') || null,
                className: el.className || null,
                xpath: el.id ? `//*[@id="${{el.id}}"]` : null,
                text: el.innerText.trim().substring(0, 100)
            }}));
        """)
        return results

    @staticmethod
    def dump_page_state(driver, filename="page_state", path="reports/screenshots"):
        # Captures everything useful about current page state in one call
        # Designed for agent consumption when debugging failures
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        state = {
            "url": driver.current_url,
            "title": driver.title,
            "data_test_elements": DebugUtils.get_all_data_test_attributes(driver),
            "interactive_elements": DebugUtils.get_interactive_elements(driver),
            "javascript_errors": DebugUtils.check_javascript_errors(driver)
        }
        import json
        filepath = f"{path}/{filename}_{timestamp}.json"
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)
        driver.save_screenshot(f"{path}/{filename}_{timestamp}.png")
        return state
