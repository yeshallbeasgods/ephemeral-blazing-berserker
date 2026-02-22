import pytest
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from pages.page_manager import PageManager
from config.settings import SauceConfig

def pytest_addoption(parser):
    parser.addoption("--custom-browser", action="store", default="chrome", help="Browser: chrome|edge|firefox")
    parser.addoption("--custom-mobile", action="store_true", default=False, help="Enable mobile emulation")
    parser.addoption("--custom-device", action="store", default="iphone_15", help="Device profile: iphone_15|android")
    parser.addoption("--custom-agent", action="store", default=None, help="Override user agent string")
    parser.addoption("--user-type", action="store", default="standard", help="User type: standard|locked_out|problem")

def _build_driver(request):
    name = request.config.getoption("--custom-browser").lower()
    mobile_flag = request.config.getoption("--custom-mobile")
    device_key = request.config.getoption("--custom-device")
    ua_override = request.config.getoption("--custom-agent")

    is_mobile_test = "mobile" in getattr(request.node, "keywords", {})
    mobile_active = mobile_flag or is_mobile_test

    device = SauceConfig.MOBILE_DEVICES.get(device_key, SauceConfig.MOBILE_DEVICES["iphone_15"])
    width = device["width"]
    height = device["height"]
    pixel_ratio = device["pixel_ratio"]
    user_agent = ua_override or device["user_agent"]

    if name == "chrome":
        options = ChromeOptions()
        if mobile_active:
            options.add_experimental_option("mobileEmulation", {
                "deviceMetrics": {"width": width, "height": height, "pixelRatio": pixel_ratio},
                "userAgent": user_agent
            })
        driver = webdriver.Chrome(options=options)

    elif name == "edge":
        options = EdgeOptions()
        options.use_chromium = True
        if mobile_active:
            options.add_experimental_option("mobileEmulation", {  # type: ignore
                "deviceMetrics": {"width": width, "height": height, "pixelRatio": pixel_ratio},
                "userAgent": user_agent
            })
        driver = webdriver.Edge(options=options)  # type: ignore

    elif name == "firefox":
        options = FirefoxOptions()
        if mobile_active and user_agent:
            options.set_preference("general.useragent.override", user_agent)
        driver = webdriver.Firefox(options=options)
        if mobile_active:
            driver.set_window_size(width, height)

    else:
        raise ValueError(f"Unsupported browser: {name}. Choose from: chrome, edge, firefox")

    if mobile_active and name in ("chrome", "edge"):
        driver.set_window_size(width, height)

    driver.implicitly_wait(SauceConfig.DEFAULT_TIMEOUT)
    return driver

@pytest.fixture(scope="function")
def browser(request):
    driver = _build_driver(request)
    yield driver
    driver.quit()

@pytest.fixture
def page_manager(browser):
    return PageManager(browser)

@pytest.fixture
def mobile_env(request, browser):
    if "mobile" not in request.node.keywords:
        return None
    try:
        ua = browser.execute_script("return navigator.userAgent;")
    except WebDriverException:
        ua = ""
    assert ("iPhone" in ua) or ("Mobile" in ua), f"Mobile user agent not applied: {ua}"
    size = browser.get_window_size()
    return {"user_agent": ua, "width": size.get("width"), "height": size.get("height")}

@pytest.fixture
def user_login(page_manager, browser, request):
    config = SauceConfig()
    user_type = request.config.getoption("--user-type")
    if user_type not in SauceConfig.USERS:
        raise ValueError(f"Invalid user type: {user_type}. Choose from {list(SauceConfig.USERS.keys())}")
    credentials = SauceConfig.USERS[user_type]
    browser.get(config.base_url)
    is_mobile = "mobile" in request.node.keywords
    if is_mobile:
        page_manager.login_page.mobile_login(
            username=credentials["username"],
            password=credentials["password"]
        )
    else:
        page_manager.login_page.login(
            username=credentials["username"],
            password=credentials["password"]
        )
    return page_manager
