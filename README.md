# Ephemeral Blazing Berserker

[![Test](https://github.com/yeshallbeasgods/ephemeral-blazing-berserker/actions/workflows/test.yml/badge.svg)](https://github.com/yeshallbeasgods/ephemeral-blazing-berserker/actions/workflows/test.yml)
[![Lint](https://github.com/yeshallbeasgods/ephemeral-blazing-berserker/actions/workflows/lint.yml/badge.svg)](https://github.com/yeshallbeasgods/ephemeral-blazing-berserker/actions/workflows/lint.yml)

A Python Selenium test automation framework targeting the [Sauce Demo](https://www.saucedemo.com) application. Built to demonstrate professional QA engineering practices including the Page Object Model, reusable utility libraries, mobile emulation, and CI/CD integration.

## Tech Stack

- Python 3.x
- Selenium WebDriver
- pytest
- webdriver-manager
- pytest-html

## Project Structure
```
ephemeral-blazing-berserker/
├── config/
│   └── settings.py                 # Environment and user configuration
├── pages/
│   ├── base_page.py                # Shared page object base class
│   ├── page_manager.py             # Central page object registry
│   ├── components/
│   │   └── header.py               # Shared header component (cart badge, nav, sort)
│   ├── mobile/
│   │   └── login_page_mobile.py
│   └── web/
│       ├── cart_page.py
│       ├── inventory_page.py
│       └── login_page.py
├── tests/
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
- Python 3.x
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
pytest -m smoke
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

Two workflows run automatically on every push and pull request to `main`:

- **Lint** — ruff checks for errors and code quality issues
- **Test** — smoke suite runs against Chrome headless; test report and failure artifacts (screenshot + page state JSON) are uploaded on every run

## Roadmap

- [x] GitHub Actions on-push workflow
- [ ] API testing with requests/httpx
- [ ] Expanded device profiles
- [ ] Allure reporting