# AGENTS.md

Selenium + pytest (Python) test suite for Sauce Demo, with web and mobile-emulation tests. Portfolio repo: correctness and readability matter more than volume.

## Commands

```bash
source venv/bin/activate          # create with: python3 -m venv venv && pip install -r requirements.txt
pytest -m "smoke and not mobile"  # what CI runs
pytest                            # everything
pytest -m mobile                  # mobile emulation only
pytest path/to/test_file.py::TestClass::test_name -v   # one test
pytest --custom-browser=chrome    # chrome | edge | firefox
pytest -m mobile --custom-device=iphone_15   # iphone_15 | android
pytest --user-type=standard       # standard | locked_out | problem
ruff check .                      # must pass before any commit
```

If a command here doesn't exist yet, say so instead of inventing it.

## Conventions (what the code won't tell you)

- Locators are class-level `UPPER_SNAKE_CASE` tuples on the page object. Dynamic ones are `@staticmethod`s returning a tuple. Tests contain no selectors.
- Prefer `data-test`, then `id`, then CSS class. Avoid XPath for static locators.
- Inside page objects use `self.driver`, never `element.parent`.
- Tests never use raw `WebDriverWait`. Use page-level waits or `WaitUtils` (imported `as wu`). DOM assertions come after a wait.
- Catch specific exceptions only. No bare `except:` or `except Exception:`, no `time.sleep`.
- Page objects inherit `BasePage`, or `HeaderComponent` if the page has the shared header. Mobile page objects subclass their web counterpart and override only what differs. `MobilePageManager` extends `PageManager`; don't mutate its attributes after construction.
- In tests, the manager from `user_login` / `mobile_login` is named `ebb` and annotated (`ebb: PageManager`) so Pylance resolves attributes.
- Plain Selenium + pytest only. No SeleniumBase.
- Every test has a marker. Mobile tests carry both `mobile` and `smoke`, so CI selects `smoke and not mobile` until the mobile suite is stable.
- Dependencies in `requirements.txt` are pinned. Dependabot opens weekly grouped PRs.
- Secrets: credentials live in `config/settings.py`; `.env` is gitignored. Never read or print `.env`. Never commit anything under `reports/`.
- Style belongs to ruff, not this file. Run it.

## Working agreement

The owner is building SDET skills through this repo, so pace matters more than speed.

1. One task at a time. Stay inside its scope.
2. Plan first. For multi-file changes, propose a short plan (files and steps) and wait for approval before editing.
3. Small steps. Do one, show it, stop for review.
4. Explain briefly. The first time a pattern appears (retry-on-stale, explicit waits, fixtures), give two or three sentences on why, plus one alternative considered.
5. Don't write pieces the owner said they will write. Offer a review instead.
6. Ask before adding a dependency, changing `pytest.ini` / `pyproject.toml`, or touching anything under `.github/`.
7. If a task is ambiguous, ask one question instead of guessing.
8. Before saying "done", run `ruff check .` and the tests that cover the change. Report what you ran and the real result. If something couldn't be run, say so.

## Debugging loop

Local: run the single failing test. On failure, `reports/screenshots/` gets a `.png` and a `.json` page-state dump (URL, `data-test` elements, interactive elements, JS errors). Read the JSON first; it usually identifies the problem without a re-run.

If it isn't enough, use `DebugUtils` (`utils/debug_utils.py`) instead of print statements or sleeps. Add the call temporarily and remove it before committing:
- Locator not found or unsure of the right one: `get_all_data_test_attributes(driver)` lists the hooks on the page, and `get_element_locator_suggestions(driver, "partial text")` suggests selectors.
- Need to see what a locator actually matches: `get_element_html(driver, locator)`.
- Need the whole picture: `dump_page_state(driver, ...)`.
- Prefer extending BrowserUtils/WaitUtils/DebugUtils over writing new one-off helpers.

Check the real method signatures in the file before using them.

CI: `gh run list --limit 5`, `gh run view <id> --log` (page state prints under "Page State on Failure"), `gh run download <id>` for the screenshot. Fix on a branch; CI must be green before merge. Never commit debug code.

## Where to look

- `README.md`: setup, structure, utility library, roadmap. Update it when commands or files change.
- `pages/`, `utils/`, `conftest.py`: read the code before adding to it. Prefer extending existing utilities.