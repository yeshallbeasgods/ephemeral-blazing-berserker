# Ephemeral Blazing Berserker

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
│   └── settings.py             # Environment and user configuration
├── pages/
│   ├── base_page.py            # Shared page object base class
│   ├── page_manager.py         # Central page object registry
│   ├── components/
│   ├── mobile/
│   └── web/
│       ├── cart_page.py
│       ├── inventory_page.py
│       └── login_page.py
├── tests/                      # Test suites (in progress)
├── utils/                      # Reusable WebDriver utilities (in progress)
├── reports/                    # Auto-generated HTML test reports
├── conftest.py                 # Fixtures and browser configuration
├── pytest.ini                  # pytest settings and markers
├── requirements.txt            # Python dependencies
├── .env                        # Local environment variables (not committed)
└── .env.example                # Environment variable template
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

## Key Features

- **Mobile emulation** via Chrome/Edge experimental options for accurate touch and JavaScript API behavior
- **Reusable utility library** including stable element waits, mobile-optimized clicks, and cross-platform keyboard handling
- **Page Object Model** with a central PageManager for scalable test organization
- **Data-driven configuration** using nested dictionaries for user profiles, device profiles, and environments
- **Cross-browser support** across Chrome, Edge, and Firefox

## CI/CD

*GitHub Actions setup coming soon.*

## Roadmap

- [ ] GitHub Actions on-push workflow
- [ ] API testing with requests/httpx
- [ ] Expanded device profiles
- [ ] Allure reporting