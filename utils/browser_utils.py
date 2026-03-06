import platform
import time
from datetime import datetime
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import NoSuchElementException, NoSuchWindowException, TimeoutException, ElementClickInterceptedException, StaleElementReferenceException, WebDriverException
from utils.wait_utils import WaitUtils

class BrowserUtils:
    @staticmethod
    def clear_and_send_keys(driver, element, text, select_all=False, delay=0.1):
        if select_all:
            modifier = Keys.COMMAND if platform.system() == "Darwin" else Keys.CONTROL
            ActionChains(driver).click(element).perform()
            time.sleep(delay)
            ActionChains(driver).key_down(modifier).send_keys("a").key_up(modifier).perform()
            time.sleep(delay)
            element.send_keys(Keys.DELETE)
            time.sleep(delay)
        else:
            element.clear()
        element.send_keys(text)

    @staticmethod
    def clear_and_send_keys_individually(element, text, delay=0.2, finish_delay=0):
        element.clear()
        for char in text:
            element.send_keys(char)
            time.sleep(delay)
        if finish_delay > 0:
            time.sleep(finish_delay)

    @staticmethod
    def switch_to_window_by_url(driver, expected_url_fragment, timeout=10, initial_delay=0):
        if initial_delay > 0:
            time.sleep(initial_delay)
        end_time = time.time() + timeout
        while time.time() < end_time:
            for handle in driver.window_handles:
                driver.switch_to.window(handle)
                if expected_url_fragment in driver.current_url:
                    return
            time.sleep(1)  # Small delay to avoid tight looping
        raise Exception(f"No window found with a URL containing '{expected_url_fragment}' within {timeout} seconds.")

@staticmethod
def switch_to_new_window(driver, known_handles, timeout=15):
    # Switches to a window that wasn't in known_handles.
    end_time = time.time() + timeout
    while time.time() < end_time:
        new = [h for h in driver.window_handles if h not in known_handles]
        if new:
            driver.switch_to.window(new[0])
            return new[0]
        time.sleep(0.5)
    raise Exception("No new window appeared within timeout")

@staticmethod
def switch_to_remaining_window(driver, timeout=10):
    end_time = time.time() + timeout
    while time.time() < end_time:
        if len(driver.window_handles) == 1:
            driver.switch_to.window(driver.window_handles[0])
            return
        time.sleep(0.5)
    handles = driver.window_handles
    titles = []
    for h in handles:
        try:
            driver.switch_to.window(h)
            titles.append(driver.title)
        except (NoSuchWindowException, WebDriverException):
            titles.append("(unreachable)")
    raise Exception(
        f"Timed out waiting for windows to close. "
        f"Still open ({len(handles)}): {titles}"
    )

@staticmethod
def close_all_except_main_window(driver, main_handle, timeout=10):
    # Closes any extra windows and returns focus to main window. Useful for headless/remote runs.
    end_time = time.time() + timeout
    while time.time() < end_time:
        extra = [h for h in driver.window_handles if h != main_handle]
        if not extra:
            driver.switch_to.window(main_handle)
            return
        for h in extra:
            try:
                driver.switch_to.window(h)
                driver.close()
            except (NoSuchWindowException, WebDriverException):
                pass
        time.sleep(0.5)
    driver.switch_to.window(main_handle)

    @staticmethod
    def javascript_click(driver, element):
        # bypasses overlays and useful with React
        driver.execute_script("arguments[0].click();", element)

    @staticmethod
    def mobile_click(driver, locator, index=None, timeout=10, wait_stable=True, stability_duration=0.3, post_click_delay=0.2):
        # a click that can wait for animations and fields in single page applications; takes a locator not an element
        if index is not None:
            element = WebDriverWait(driver, timeout).until(lambda d: d.find_elements(*locator)[index] if len(d.find_elements(*locator)) > index else False)
        else:
            element = WebDriverWait(driver, timeout).until(ec.element_to_be_clickable(locator))
        if wait_stable:
            WaitUtils.wait_for_element_stable(driver, locator, timeout=3, stability_duration=stability_duration)
            element = driver.find_elements(*locator)[index] if index is not None else driver.find_element(*locator)
        ActionChains(driver).double_click(element).perform()
        if post_click_delay > 0:
            time.sleep(post_click_delay)

    @staticmethod
    def click_at_coordinates(driver, x, y):
        ActionChains(driver).move_by_offset(x, y).click().perform()

    @staticmethod
    def safe_click(driver, element, timeout=10):
        # a click with a clickable waits built in; takes an element, not a locator
        try:
            WebDriverWait(driver, timeout).until(ec.visibility_of(element))
            WebDriverWait(driver, timeout).until(ec.element_to_be_clickable(element)).click()
        except TimeoutException:
            raise TimeoutException(f"{element} was not clickable within {timeout} seconds.")

    @staticmethod
    def robust_click(driver, element, timeout=10, retries=3):
        # a click for dealing with timing issues and race conditions; if this fails use retry_interaction
        # takes an element, not a locator
        for attempt in range(retries):
            try:
                WebDriverWait(driver, timeout).until(ec.visibility_of(element))
                WebDriverWait(driver, timeout).until(ec.element_to_be_clickable(element)).click()
                return
            except (ElementClickInterceptedException, StaleElementReferenceException):
                if attempt < retries - 1:
                    time.sleep(0.5)  # Small delay before retrying
                else:
                    raise ElementClickInterceptedException(f"Failed to click {element} after {retries} attempts.")
            except TimeoutException:
                raise TimeoutException(f"{element} was not clickable within {timeout} seconds.")

    @staticmethod
    def click_with_offset(driver, element, x_offset=0, y_offset=0):
        ActionChains(driver).move_to_element_with_offset(element, x_offset, y_offset).click().perform()

    @staticmethod
    def double_click(driver, element, timeout=10): 
        WebDriverWait(driver, timeout).until(ec.element_to_be_clickable(element))
        ActionChains(driver).double_click(element).perform()

    @staticmethod
    def right_click(driver, element):
        ActionChains(driver).context_click(element).perform()

    @staticmethod
    def tap_at_coordinates(driver, x, y):
        # For overlapping elements
        actions = ActionChains(driver)
        actions.w3c_actions.pointer_action.move_to_location(x, y)
        actions.w3c_actions.pointer_action.click()
        actions.perform()

    @staticmethod
    def hover(driver, element, duration=0):
        ActionChains(driver).move_to_element(element).perform()
        if duration > 0:
            time.sleep(duration)

    @staticmethod
    def scroll_to_element(driver, element):
        driver.execute_script("arguments[0].scrollIntoView(true);", element)

    @staticmethod
    def scroll_to_top(driver):
        driver.execute_script("window.scrollTo(0, 0);")

    @staticmethod
    def scroll_to_bottom(driver):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    @staticmethod
    def scroll_until_visible(driver, locator, timeout=10, scroll_pause=0.5):
        end_time = time.time() + timeout
        while time.time() < end_time:
            try:
                element = driver.find_element(*locator)
                if element.is_displayed():
                    return element
            except (NoSuchElementException, StaleElementReferenceException):
                pass
            driver.execute_script("window.scrollBy(0, 300);")
            time.sleep(scroll_pause)
        raise TimeoutException(f"{locator} not found after scrolling for {timeout}s")

    @staticmethod
    def highlight_element(driver, element):
        driver.execute_script("arguments[0].style.border='3px solid red'", element)

    @staticmethod
    def get_element_screenshot(element, filename):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        element.screenshot(f"screenshots/{filename}_{timestamp}.png")

    @staticmethod
    def remove_element(driver, element):
        # for removing an element, like a pop-up or overlay, from the DOM; use with caution
        driver.execute_script("arguments[0].remove();", element)

    @staticmethod
    def select_dropdown_by_text(driver, locator, text):
        # select dropdown option by visible text
        dropdown = Select(WebDriverWait(driver, 10).until(ec.presence_of_element_located(locator)))
        dropdown.select_by_visible_text(text)