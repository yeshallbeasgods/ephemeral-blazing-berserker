import time
import requests
from requests import RequestException
from selenium.webdriver import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementNotInteractableException, \
    ElementClickInterceptedException, StaleElementReferenceException
from selenium.webdriver.support import expected_conditions as ec
from utils.debug_utils import DebugUtils

class WaitUtils:
    @staticmethod
    def wait_for_element(driver, element, condition, timeout=10):
        # Common expected conditions include ec.visibility_of, ec.element_to_be_clickable, ec.invisibility_of_element
        # Takes a WebElement, not a locator
        try:
            WebDriverWait(driver, timeout).until(condition(element))
            return element
        except TimeoutException:
            raise TimeoutException(f"The {element} didn't meet your condition within {timeout} seconds.")

    @staticmethod
    def fluent_wait_for_element(driver, element, condition, timeout=10, poll_frequency=0.5):
        # Common expected conditions include ec.visibility_of, ec.element_to_be_clickable, ec.invisibility_of_element
        # Takes a WebElement, not a locator
        try:
            WebDriverWait(driver, timeout, poll_frequency, ignored_exceptions=[NoSuchElementException]).until(condition(element))
            return element
        except TimeoutException:
            raise TimeoutException(f"The {element} didn't meet your condition within {timeout} seconds.")

    @staticmethod
    def wait_for_element_to_disappear(driver, element, timeout=10):
        # Use if wait for element to be invisible doesn't work
        WebDriverWait(driver, timeout).until_not(ec.visibility_of(element))

    @staticmethod
    def wait_for_url_to_contain(driver, string, timeout=10):
        WebDriverWait(driver, timeout).until(ec.url_contains(string))

    @staticmethod
    def wait_for_page_load(driver, timeout=30):
        WebDriverWait(driver, timeout).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )

    @staticmethod
    def wait_for_new_window(driver, window_count=2, timeout=10, debug=False):
        try:
            WebDriverWait(driver, timeout).until(lambda d: len(d.window_handles) >= window_count)
            if debug:
                DebugUtils.print_window_handles(driver)
        except TimeoutException:
            raise TimeoutException(f"A new window did not appear. {window_count} window(s) were expected.")

    @staticmethod
    def wait_for_text_in_dom(driver, text, timeout=5):
        # this is a bad test and should only be used if element is completely unavailable
        WebDriverWait(driver, timeout).until(
            lambda d: text in d.page_source,
            f"Your string '{text}' was not found in the DOM within {timeout} seconds."
        )

    @staticmethod
    def wait_for_api_response(url, headers=None, timeout=30, interval=1):
        end_time = time.time() + timeout
        while time.time() < end_time:
            try:
                response = requests.get(url, headers=headers)
                if response.status_code == 200:
                    return response
            except RequestException as e:
                print(f"Error while making request: {e}")
            time.sleep(interval)
        raise TimeoutError(f"Timed out waiting for a 200 response from {url}")

    @staticmethod
    def wait_for_element_stable(driver, locator, timeout=5, poll_interval=0.1, stability_duration=0.3):
        stable_since = None
        last_location = None
        last_size = None
        end_time = time.time() + timeout
        while time.time() < end_time:
            try:
                element = driver.find_element(*locator)  # re-fetch each cycle
                current_location = element.location
                current_size = element.size
            except StaleElementReferenceException:
                stable_since = None
                time.sleep(poll_interval)
                continue
            if current_location == last_location and current_size == last_size:
                if stable_since is None:
                    stable_since = time.time()
                elif time.time() - stable_since >= stability_duration:
                    return
            else:
                stable_since = None
                last_location = current_location
                last_size = current_size
            time.sleep(poll_interval)
        raise TimeoutException(f"Element {locator} did not stabilize within {timeout}s")

    @staticmethod
    def wait_for_element_count(driver, locator, count, timeout=10):
        WebDriverWait(driver, timeout).until(
            lambda d: len(d.find_elements(*locator)) >= count
        )

    @staticmethod
    def wait_for_network_idle(driver, timeout=5):
        # Wait for all network requests to finish (useful after navigation).
        # Does not catch XHR/fetch requests after page load, only static resources; combine with other waits as needed.
        WebDriverWait(driver, timeout).until(
            lambda d: d.execute_script(
                "return window.performance.getEntriesByType('resource')"
                ".filter(r => r.responseEnd === 0).length === 0;"
            )
        )

    @staticmethod
    def wait_for_animations_complete(driver, timeout=5):
        WebDriverWait(driver, timeout).until(
            lambda d: d.execute_script(
                "return document.getAnimations().every(a => a.playState === 'finished');"
            )
        )

    @staticmethod
    def retry_interaction(element, action, timeout=10, interval=0.5):
        # use if robust_click fails
        # an action can be a callable that interacts with the element, such as sending keys or clicking
        end_time = time.time() + timeout
        while time.time() < end_time:
            try:
                action(element)
                return
            except (ElementNotInteractableException, ElementClickInterceptedException):
                time.sleep(interval)
        raise Exception(f"Failed to interact with the element within {timeout} seconds.")

    @staticmethod
    def swipe(driver, start_x, start_y, end_x, end_y, duration=1000):
        # swipe gesture for navigating carousels, drawers, infinite scrolls
        actions = ActionChains(driver)
        actions.w3c_actions.pointer_action.move_to_location(start_x, start_y)
        actions.w3c_actions.pointer_action.pointer_down()
        actions.w3c_actions.pointer_action.pause(duration / 1000)
        actions.w3c_actions.pointer_action.move_to_location(end_x, end_y)
        actions.w3c_actions.pointer_action.pointer_up()
        actions.perform()