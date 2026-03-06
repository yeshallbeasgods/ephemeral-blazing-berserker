# AGENTS.md — Ephemeral Blazing Berserker

Guidance for AI agents working on this repository.

---

## Project Overview

A Python Selenium test automation framework targeting [Sauce Demo](https://www.saucedemo.com). Demonstrates professional QA engineering practices: Page Object Model, shared component inheritance, reusable utility libraries, mobile emulation, and CI/CD via GitHub Actions.

**In progress:**
- `pages/mobile/mobile_page_manager.py` — `MobilePageManager` subclass needed (referenced in `conftest.py`)
- `pages/mobile/login_page_mobile.py` — mobile login page object needed
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

## Coding Standards

- **Page objects** must inherit from `BasePage` (directly or via `HeaderComponent`)
- **Mobile page objects** inherit from their web counterpart and override only the methods that differ — use `BrowserUtils.mobile_click` for interactions
- **`MobilePageManager`** subclasses `PageManager` and swaps in mobile page objects; do not mutate `PageManager` attributes after construction
- **Waits**: use `WaitUtils` methods or page-level wait methods (e.g. `wait_for_cart_count`) — do not use raw `ebb.wait.until(ec.url_contains(...))` in tests; use `wu.wait_for_url_to_contain(browser, "fragment")` instead
- **Exceptions**: never use bare `except:` or broad `except Exception:` — catch specific exception types (e.g. `NoSuchElementException`, `ValueError`)
- **Type annotations**: fixtures in `conftest.py` must have `-> PageManager` (or appropriate) return type annotations so Pylance resolves types in tests
- **Imports**: do not leave unused imports; ruff enforces this on every push

---

## Testing Instructions

- All tests must be tagged with at least one marker: `@pytest.mark.smoke` or `@pytest.mark.mobile`
- Mobile tests use the `mobile_login` fixture; desktop tests use `user_login`
- Tests should not contain raw `WebDriverWait` calls — use `WaitUtils` or page-level methods
- Assertions on DOM state (badge counts, page titles) must be preceded by an appropriate wait
- The `browser` fixture is function-scoped — each test gets a clean browser instance

---

## Debugging Failing Tests

`DebugUtils` in `utils/debug_utils.py` includes a suite of tools built specifically for agent use. Follow this protocol when investigating a failure:

### Step 1 — Check automatic artifacts first

On any test failure, `conftest.py` automatically calls `dump_page_state`, which writes two files to `reports/screenshots/`:

- `{test_name}_{timestamp}.png` — screenshot of the browser at time of failure
- `{test_name}_{timestamp}.json` — full page state snapshot including:
  - Current URL and page title
  - All elements with `data-test` attributes (the locator hooks used throughout this codebase)
  - All interactive elements (buttons, inputs, links)
  - Any JavaScript console errors

Read the JSON artifact before doing anything else. It often contains enough information to identify the problem without running the tests again.

### Step 2 — Add targeted debug calls if needed

If the artifact isn't sufficient, temporarily add calls inside the failing test or page object method, re-run the specific test, then remove them before committing.

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

### Step 3 — Run the isolated test

```bash
pytest tests/web/test_cart_smoke.py::TestCartSmoke::test_add_single_item_to_cart -v
```

### Step 4 — Remove debug calls before committing

Debug calls must not be left in committed code. Once the fix is confirmed, remove all temporary `DebugUtils` calls.

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
