from utils.allure_environment import write_environment_properties

LOCAL = {"SECRET_TOKEN": "hunter2", "PASSWORD": "hunter2"}
CI = {
    **LOCAL,
    "GITHUB_REPOSITORY": "owner/repo",
    "GITHUB_RUN_ID": "42",
    "GITHUB_SERVER_URL": "https://github.com",
}


def read(tmp_path, env):
    path = write_environment_properties(tmp_path / "allure-results", "chrome", "https://www.saucedemo.com", env)
    return path.read_text()


def test_writes_browser_url_and_python(tmp_path):
    text = read(tmp_path, LOCAL)
    assert "Browser=chrome\n" in text
    assert "Base\\ URL=https://www.saucedemo.com\n" in text
    assert "Python=3." in text


def test_run_url_only_when_running_in_ci(tmp_path):
    assert "CI" not in read(tmp_path, LOCAL)
    assert "CI\\ run=https://github.com/owner/repo/actions/runs/42\n" in read(tmp_path, CI)


def test_never_writes_other_environment_values(tmp_path):
    assert "hunter2" not in read(tmp_path, CI)
