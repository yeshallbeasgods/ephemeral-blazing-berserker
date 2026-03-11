# AGENTS.md — Ephemeral Blazing Berserker

Guidance for AI agents working on this repository.

---

## Project Overview

A Python Selenium test automation framework targeting [Sauce Demo](https://www.saucedemo.com). Demonstrates professional QA engineering practices: Page Object Model, shared component inheritance, reusable utility libraries, mobile emulation, and CI/CD via GitHub Actions.

**In progress:**
- `pages/mobile/login_page_mobile.py` — mobile login page object still needed
- Mobile test coverage is being built out under `tests/mobile/`

---

## Build and Test Commands

```bash
# Activate virtual environment first
source venv/bin/activate

# Run all tests
pytest

# Run smoke suite only (used in CI)
pytest -m smoke

# Run mobile tests only
pytest -m mobile

# Run web tests only
pytest -m "not mobile"

# Run specific browser
pytest --custom-browser=chrome   # chrome | edge | firefox

# Run specific device profile (mobile only)
pytest -m mobile --custom-device=iphone_15   # iphone_15 | android

# Run as a specific user type
pytest --user-type=standard   # standard | locked_out | problem

# Lint
ruff check .
```

---

## Architecture

```
pages/
  base_page.py              # All page objects inherit from this
  page_manager.py           # Registry of web page objects; used by user_login fixture
  components/header.py      # Shared header (cart badge, nav); web pages inherit this
  web/                      # Desktop page objects
  mobile/                   # Mobile page objects — override interactions using BrowserUtils

utils/
  browser_utils.py          # Interaction helpers (clicks, scroll, keyboard, windows)
  wait_utils.py             # Explicit wait strategies and polling helpers
  debug_utils.py            # Human debugging tools + agent/CI inspection tools

tests/
  web/                      # Desktop smoke tests
  mobile/                   # Mobile smoke tests — use mobile_login fixture

conftest.py                 # Fixtures: browser, page_manager, user_login, mobile_login
```

---

## Naming Conventions

### Locator constants

Locators are defined as **class-level `UPPER_SNAKE_CASE` tuples** on the page object, never inline inside methods or tests:

```python
# Correct — class-level constant
class LoginPage(BasePage):
    USERNAME_INPUT = (By.CSS_SELECTOR, "[data-test='username']")

    def enter_username(self, value):
        self.driver.find_element(*self.USERNAME_INPUT).send_keys(value)
```

Use `data-test` attributes as the preferred selector strategy. Fall back to `id`, then CSS class only when `data-test` is absent on the target element. Avoid XPath for static locators.

### Dynamic locators

When the selector depends on runtime data (e.g. a product name), define a `@staticmethod` that returns the tuple:

```python
@staticmethod
def add_to_cart_locator(item_name: str) -> tuple:
    slug = item_name.lower().replace(" ", "-")
    return By.CSS_SELECTOR, f"[data-test='add-to-cart-{slug}']"
```

Call it with `self.add_to_cart_locator(name)` inside the page object method — never generate the locator inside a test.

### Import aliases

| Import | Alias | Usage |
|---|---|---|
| `from utils.wait_utils import WaitUtils` | `as wu` | `wu.wait_for_url_to_contain(browser, "fragment")` |

`WaitUtils` is imported `as wu` throughout tests and page objects. `BrowserUtils` is imported unaliased (`BrowserUtils.mobile_click(...)`).

### Test variable name for PageManager

Inside test methods, the `PageManager` instance received from `user_login` or `mobile_login` is assigned to `ebb`:

```python
def test_example(self, user_login, browser):
    ebb: PageManager = user_login
    ebb.inventory_page.add_to_cart("Sauce Labs Backpack")
```

The type annotation (`ebb: PageManager`) is required so Pylance resolves page object attributes.

---

## Coding Standards

- **Page objects** must inherit from `BasePage` (directly or via `HeaderComponent`). Use `HeaderComponent` for any page that has the shared navigation bar, cart icon, or sort control (e.g. `InventoryPage`, `CartPage`). Use `BasePage` directly for standalone pages that do not share that chrome (e.g. `LoginPage`).
- **Mobile page objects** inherit from their web counterpart and override only the methods that differ — use `BrowserUtils.mobile_click` for interactions
- **`MobilePageManager`** subclasses `PageManager` and swaps in mobile page objects; do not mutate `PageManager` attributes after construction
- **Waits**: use `WaitUtils` methods or page-level wait methods (e.g. `wait_for_cart_count`) — do not use raw `ebb.wait.until(ec.url_contains(...))` in tests; use `wu.wait_for_url_to_contain(browser, "fragment")` instead
- **Exceptions**: never use bare `except:` or broad `except Exception:` — catch specific exception types (e.g. `NoSuchElementException`, `ValueError`)
- **Type annotations**: fixtures in `conftest.py` must have `-> PageManager` (or appropriate) return type annotations so Pylance resolves types in tests
- **Imports**: do not leave unused imports; ruff enforces this on every push

---

## What Not To Do

- **No SeleniumBase.** This project uses plain Selenium + pytest. Do not import or reference `seleniumbase`, `SB`, `BaseCase`, or any SeleniumBase primitives.
- **No `element.parent` to get the driver.** Always use `self.driver` (inherited from `BasePage`) inside page objects. `WebElement.parent` is an internal Selenium detail and must not be relied upon.
- **No inline locators in tests.** Tests must not contain `By.CSS_SELECTOR`, `By.ID`, or any selector string. All locators belong as constants or `@staticmethod` methods on the relevant page object class.
- **No raw `WebDriverWait` in tests.** Use `wu.wait_for_url_to_contain(browser, ...)` or page-level wait methods (e.g. `wait_for_cart_count`). Raw `WebDriverWait(driver, 10).until(...)` calls belong inside page objects or utilities only.

---

## Fixtures

All fixtures are defined in `conftest.py` and are function-scoped unless noted.

| Fixture | Yields | Use when |
|---|---|---|
| `browser` | `WebDriver` | Low-level driver access; rarely used directly in tests |
| `page_manager` | `PageManager` | You need a `PageManager` without a pre-logged-in session |
| `user_login` | `PageManager` (logged in) | Desktop tests — yields a `PageManager` already past the login screen |
| `mobile_login` | `MobilePageManager` (logged in) | Mobile tests — same as `user_login` but via `MobilePageManager` |
| `mobile_env` | `dict` (viewport info) | Validates mobile UA is applied; consumed internally by `mobile_login` |

The `--user-type` CLI option (standard / locked_out / problem) controls which Sauce Demo account `user_login` and `mobile_login` authenticate with. Default is `standard`.

---

## Testing Instructions

- All tests must be tagged with at least one marker: `@pytest.mark.smoke` or `@pytest.mark.mobile`
- Mobile tests use the `mobile_login` fixture; desktop tests use `user_login`
- Tests should not contain raw `WebDriverWait` calls — use `WaitUtils` or page-level methods
- Assertions on DOM state (badge counts, page titles) must be preceded by an appropriate wait
- The `browser` fixture is function-scoped — each test gets a clean browser instance
- CI runs `pytest -m smoke` and generates two report artifacts (gitignored, never committed):
  - `reports/test-report.html` — pytest-html full run report
  - `reports/screenshots/{test_name}_{timestamp}.png/.json` — auto-captured on any test failure

---

## Debugging Failing Tests

`DebugUtils` in `utils/debug_utils.py` includes a suite of tools built specifically for agent use. The debugging workflow differs depending on whether you are working locally or investigating a CI failure.

---

### Local Debugging

When working locally, agents can run tests directly and read output and artifacts without any extra steps.

**Run a specific failing test:**
```bash
pytest tests/web/test_cart_smoke.py::TestCartSmoke::test_add_single_item_to_cart -v
pytest tests/mobile/test_cart_mobile.py::TestCartMobile::test_add_single_item_to_cart -v
```

**On failure, two files are automatically written to `reports/screenshots/`:**
- `{test_name}_{timestamp}.png` — screenshot at time of failure
- `{test_name}_{timestamp}.json` — full page state including URL, title, all `data-test` elements, interactive elements, and JS errors

Read the JSON file first. It usually contains enough to identify the problem without running again.

**If the artifact isn't sufficient, temporarily add debug calls inside the failing test or page object method, re-run, then remove before committing:**

```python
from utils.debug_utils import DebugUtils

# Map what data-test hooks are available on the current page
print(DebugUtils.get_all_data_test_attributes(driver))

# Verify a specific locator resolves correctly
print(DebugUtils.get_element_html(driver, (By.CSS_SELECTOR, "[data-test='add-to-cart-sauce-labs-backpack']")))

# Find elements by visible text (useful when data-test attribute is unknown)
print(DebugUtils.find_elements_by_text(driver, "Add to cart"))

# Get all interactive elements on the page
print(DebugUtils.get_interactive_elements(driver))

# Suggest locators based on partial text match
print(DebugUtils.get_element_locator_suggestions(driver, "Backpack"))
```

Debug calls must not be left in committed code.

---

### CI Debugging (GitHub Actions)

When a test fails in CI, the full page state JSON is printed directly to the job logs — no artifact download needed. Fetch the logs with:

```bash
# List recent runs
gh run list --limit 5

# View logs for a specific run
gh run view <run-id> --log

# Filter to just the failed test output
gh run view <run-id> --log | grep -A 100 "Page State on Failure"
```

The log output will contain the same JSON that would be written locally to `reports/screenshots/` — URL, page title, all `data-test` elements, interactive elements, and JS errors.

Artifacts (screenshot + JSON file) are also uploaded and retained for 7 days. Download them if you need the screenshot:

```bash
gh run download <run-id> --dir reports/
```

---

## Dependency Policy

- All dependencies in `requirements.txt` must be pinned to an exact version
- Dependabot runs weekly and groups all pip updates into a single PR
- Do not add new dependencies without a clear need; prefer extending existing utilities

---

## Security

- Credentials are never hardcoded — they live in `config/settings.py` under `SauceConfig.USERS`
- `.env` is gitignored; use `.env.example` as the template
- Do not commit screenshots, HTML reports, or JSON artifacts — these are gitignored under `reports/`

---

## Documentation

- Update `README.md` Project Structure when adding or removing files
- Update the Utility Library section in `README.md` when adding new utility methods
- Roadmap items should be checked off (`- [x]`) when completed
