from pathlib import Path

# Allure groups tests by epic > feature > story. Instead of labelling every test by hand, they are
# derived from where the test lives: the folder under tests/ is the epic and the file is the feature.
# The story is the test name.

EPICS = {
    "web": "Web UI",
    "mobile": "Mobile",
    "api": "API",
}

FEATURES = {
    "test_login_smoke.py": "Login",
    "test_mobile_login.py": "Login",
    "test_cart_smoke.py": "Cart",
    "test_cart_mobile.py": "Cart",
    "test_openweather.py": "Current weather",
}


def labels_for(test_file) -> tuple[str, str]:
    """Return (epic, feature) for a test file under tests/."""
    path = Path(test_file)
    folders = path.parts[:-1]
    # The last "tests" folder, so a checkout that itself sits under a tests/ directory still works
    last_tests = len(folders) - 1 - folders[::-1].index("tests") if "tests" in folders else None
    folder = folders[last_tests + 1] if last_tests is not None and last_tests + 1 < len(folders) else ""
    # An unmapped file still gets a readable feature name, e.g. "test_wishlist_smoke.py" -> "Wishlist smoke"
    fallback = path.stem.removeprefix("test_").replace("_", " ").capitalize()
    return EPICS.get(folder, "Other"), FEATURES.get(path.name, fallback)
