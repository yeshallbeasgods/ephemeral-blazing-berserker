# Selenium + Python (pytest) Test Automation
Web and mobile-emulation smoke tests (Sauce Demo), a custom utility library, and GitHub Actions CI. Work in progress.

[![CI](https://github.com/yeshallbeasgods/ephemeral-blazing-berserker/actions/workflows/ci.yml/badge.svg)](https://github.com/yeshallbeasgods/ephemeral-blazing-berserker/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A Python Selenium test automation framework targeting the [Sauce Demo](https://www.saucedemo.com) application. Built to demonstrate professional QA engineering practices including the Page Object Model, reusable utility libraries, mobile emulation, and CI/CD integration.

## The Utility Library in Action

Tests contain no selectors and no waits. The timing logic lives in the utility library, behind the page objects, so a test reads like the user journey:

```python
# tests/web/test_cart_smoke.py
ebb.inventory_page.add_to_cart("Sauce Labs Backpack")
ebb.inventory_page.wait_for_cart_count(1)
ebb.inventory_page.cart_icon().click()
wu.wait_for_url_to_contain(browser, "cart")
assert "Sauce Labs Backpack" in ebb.cart_page.get_cart_item_names()
```

In mobile emulation, the same journey needs a click that survives animations in a single-page app. The mobile page object overrides only that one method and delegates to `BrowserUtils`, which waits for the element to be clickable and for its position and size to stop changing (`WaitUtils.wait_for_element_stable`) before it acts:

```python
# pages/mobile/inventory_page_mobile.py
class MobileInventoryPage(InventoryPage):
    def add_to_cart(self, item_name):
        locator = self.add_to_cart_locator(item_name)
        BrowserUtils.mobile_click(self.driver, locator)
```

`mobile_click` prevents timing problems by waiting before it acts. `BrowserUtils.robust_click` handles the other kind: a click that fails because the page changed underneath it. It waits for the element to be visible and clickable, and if the click is intercepted by an overlay or the element goes stale because the DOM re-rendered, it retries a limited number of times before raising a clear error:

```python
# utils/browser_utils.py (core of robust_click)
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
```

It catches only the two exceptions that mean "try again" and lets everything else fail immediately, so a real bug is not hidden by a retry. A page object would call it as `BrowserUtils.robust_click(self.driver, element)`; the current page objects don't need it yet.

When a test fails, `DebugUtils.dump_page_state` runs automatically from a pytest hook in `conftest.py`. It saves a screenshot and a JSON snapshot of the page (an abbreviated example):

```json
{
  "url": "https://www.saucedemo.com/inventory.html",
  "title": "Swag Labs",
  "data_test_elements": [
    { "dataTest": "shopping-cart-link", "tag": "A", "visible": true }
  ],
  "interactive_elements": ["..."],
  "javascript_errors": []
}
```

In CI the snapshot is also printed to the job log, so a failure can usually be diagnosed without re-running. Details on each utility are in [Utility Library](#utility-library) below.

## Tech Stack

- Python 3.13
- Selenium WebDriver
- pytest
- webdriver-manager
- pytest-html
- ruff

## Project Structure
```
ephemeral-blazing-berserker/
├── .github/
│   └── workflows/
│       └── ci.yml                  # Lint, smoke tests, report, and Pages publish
├── config/
│   └── settings.py                 # Environment and user configuration
├── pages/
│   ├── base_page.py                # Shared page object base class
│   ├── page_manager.py             # Central page object registry
│   ├── components/
│   │   └── header.py               # Shared header component (cart badge, nav, sort)
│   ├── mobile/
│   │   ├── inventory_page_mobile.py
│   │   └── mobile_page_manager.py
│   └── web/
│       ├── cart_page.py
│       ├── inventory_page.py
│       └── login_page.py
├── scripts/
│   ├── build_status.py             # Builds status.json from the pytest junit XML
│   └── test_build_status.py        # Tests for build_status.py (run separately, see CI/CD)
├── site/
│   └── index.html                  # Pages root; redirects to report/
├── tests/
│   ├── mobile/
│   │   └── test_cart_mobile.py
│   └── web/
│       ├── test_cart_smoke.py
│       └── test_login_smoke.py
├── utils/
│   ├── browser_utils.py            # Interaction helpers (clicks, scroll, keyboard, windows)
│   ├── wait_utils.py               # Explicit wait strategies and polling helpers
│   └── debug_utils.py             # Debugging and inspection utilities (see below)
├── reports/                        # Auto-generated HTML test reports
├── conftest.py                     # Fixtures and browser configuration
├── pytest.ini                      # pytest settings and markers
├── requirements.txt                # Python dependencies
├── .env                            # Local environment variables (not committed)
└── .env.example                    # Environment variable template
```

## Setup

### Prerequisites
- Python 3.13
- Google Chrome, Microsoft Edge, or Firefox

### Installation

Clone the repository:
```bash
git clone https://github.com/yeshallbeasgods/ephemeral-blazing-berserker.git
cd ephemeral-blazing-berserker
```

Create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows
```

Install dependencies:
```bash
pip install -r requirements.txt
```

Set up environment variables:
```bash
cp .env.example .env
```

## Running Tests

### Run all tests
```bash
pytest
```

### Run with a specific browser
```bash
pytest --custom-browser=chrome
pytest --custom-browser=edge
pytest --custom-browser=firefox
```

### Run mobile tests only
```bash
pytest -m mobile
```

### Run desktop tests only
```bash
pytest -m "not mobile"
```

### Run smoke tests only
```bash
pytest -m "smoke and not mobile"   # what CI runs
```

### Run with a specific device profile
```bash
pytest -m mobile --custom-device=iphone_15
pytest -m mobile --custom-device=android
```

### Run as a specific user type
```bash
pytest --user-type=standard
pytest --user-type=locked_out
pytest --user-type=problem
```

### Combine options
```bash
pytest -m mobile --custom-browser=chrome --custom-device=android --user-type=problem -k "test_add_to_cart"
```

### Generate HTML report
Reports are generated automatically after every run at:
```
reports/test-report.html
```

## Test Markers

| Marker | Description |
|--------|-------------|
| `mobile` | Tests running in mobile emulation mode |
| `smoke` | Core user journey smoke tests |

## Utility Library

### BrowserUtils
Interaction helpers for complex click scenarios, keyboard input, scrolling, and window/tab management. Includes `mobile_click` (animation-aware, SPA-safe), `robust_click` (retry with stale element handling), `javascript_click` (overlay bypass), and cross-platform keyboard utilities.

### WaitUtils
Explicit wait strategies beyond standard `WebDriverWait`. Includes fluent waits, element stability polling (position/size), network idle detection, animation completion checks, and API response polling.

### DebugUtils
Two categories of debugging support:

**Human debugging** — tools for investigating failures locally: screenshots, page source capture, element detail printing, console log and network request inspection, and `capture_page_state` (screenshot + HTML in one call).

**Agent/CI debugging** — tools designed for coding agents and CI pipelines diagnosing failures without a browser: `get_all_data_test_attributes` (maps available test hooks on the page), `get_interactive_elements` (all clickable targets), `get_element_locator_suggestions` (finds elements by partial text to help fix broken selectors), and `dump_page_state` (full JSON snapshot of URL, elements, and JS errors alongside a screenshot).

## Key Features

- **Mobile emulation** via Chrome/Edge experimental options for accurate touch and JavaScript API behavior
- **Component-based page objects** with a shared `HeaderComponent` providing cart badge, navigation, and sort across all pages
- **Page Object Model** with a central `PageManager` for scalable test organization
- **Data-driven configuration** using nested dictionaries for user profiles, device profiles, and environments
- **Cross-browser support** across Chrome, Edge, and Firefox

## CI/CD

One workflow, `ci.yml`, runs on every push and pull request to `main`, nightly at 11:41 UTC, and on demand:

- **Lint** — ruff, plus the tests for `scripts/build_status.py`
- **Smoke tests** — web smoke suite (mobile tests excluded until the mobile suite is stable) against Chrome headless; on failure, full page state (URL, DOM elements, JS errors) is printed to the job logs and artifacts (screenshot + JSON) are uploaded and retained for 14 days
- **Report** — builds the site from the test results, even when tests fail
- **Publish** — pushes the site to GitHub Pages (`main` and nightly runs only, never pull requests)

### Published site

https://yeshallbeasgods.github.io/ephemeral-blazing-berserker/

| Path | Contents |
|------|----------|
| `report/` | pytest-html report from the latest run |
| `status.json` | Machine-readable run summary (schema 1, shared by my other test repos): overall result, per-job results, test counts, commit and run links |

`scripts/build_status.py` builds `status.json` from the pytest junit XML. Run its tests with `pytest scripts -o addopts=""`.

## License

MIT — see [LICENSE](LICENSE) for details.

## Roadmap

**Complete**
- [x] Web smoke tests — login and cart flows
- [x] Utility library — BrowserUtils, WaitUtils, DebugUtils
- [x] Mobile emulation with MobilePageManager and mobile page object layer
- [x] GitHub Actions CI — lint and test workflows on push and PR
- [x] Failure artifacts — screenshot and page state JSON captured automatically on test failure

**In progress**
- [ ] Mobile smoke tests — login and cart flows via mobile_login fixture and MobileHeaderComponent

**Upcoming**
- [ ] API tests — OpenWeather current weather endpoint using requests; parametrized cities, schema validation, environment-managed API key
- [ ] Data-driven tests — SQLite fixtures for product test data, replacing hardcoded strings in cart assertions
- [ ] Allure reporting — rich test reports with screenshot attachments alongside existing pytest-html
