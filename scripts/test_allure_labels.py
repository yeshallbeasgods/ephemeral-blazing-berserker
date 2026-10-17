from utils.allure_labels import labels_for


def test_known_files_use_the_mapped_names():
    assert labels_for("/repo/tests/web/test_cart_smoke.py") == ("Web UI", "Cart")
    assert labels_for("/repo/tests/mobile/test_cart_mobile.py") == ("Mobile", "Cart")
    assert labels_for("/repo/tests/api/test_openweather.py") == ("API", "Current weather")


def test_unmapped_file_gets_a_readable_feature():
    assert labels_for("/repo/tests/web/test_wishlist_smoke.py") == ("Web UI", "Wishlist smoke")


def test_unmapped_folder_is_other():
    assert labels_for("/repo/tests/visual/test_cart_smoke.py") == ("Other", "Cart")


def test_a_repo_checked_out_under_a_tests_folder_is_not_confused():
    assert labels_for("/home/me/tests/ephemeral/tests/web/test_login_smoke.py") == ("Web UI", "Login")
