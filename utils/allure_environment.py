import platform
from pathlib import Path


def write_environment_properties(alluredir, browser, base_url, env) -> Path:
    """Write allure-results/environment.properties, which Allure shows on the report overview.

    Only fixed, non-secret facts are written. `env` is read for the GITHUB_* run identifiers and
    nothing else; it is never copied wholesale.
    """
    properties = {
        "Browser": browser,
        "Base URL": base_url,
        "Python": platform.python_version(),
    }
    if env.get("GITHUB_REPOSITORY") and env.get("GITHUB_RUN_ID"):
        server = env.get("GITHUB_SERVER_URL", "https://github.com")
        properties["CI run"] = f"{server}/{env['GITHUB_REPOSITORY']}/actions/runs/{env['GITHUB_RUN_ID']}"

    path = Path(alluredir) / "environment.properties"
    path.parent.mkdir(parents=True, exist_ok=True)
    # Spaces in keys must be escaped in a .properties file
    path.write_text("".join(f"{key.replace(' ', chr(92) + ' ')}={value}\n" for key, value in properties.items()))
    return path
