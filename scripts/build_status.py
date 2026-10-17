"""Writes the status.json that the portfolio hub reads (schema 1). Run by CI after the tests:

    python scripts/build_status.py reports/junit.xml publish/status.json

Job results arrive as LINT_RESULT / SMOKE_RESULT (the values of `needs.<job>.result`).
"""

import json
import os
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path


def _outcome(case: ET.Element) -> str:
    """Map one <testcase> to passed / failed / broken / skipped."""
    if case.find("failure") is not None:
        return "failed"
    if case.find("error") is not None:
        return "broken"
    skipped = case.find("skipped")
    if skipped is None or skipped.get("type") == "pytest.xfail":
        return "passed"
    return "skipped"


def count_tests(junit_path: Path) -> dict:
    """Return {"total", "passed", "failed", "broken", "skipped", "flaky"} from a pytest junit XML file.

    Rules (agreed for the shared contract):
      - Each test counts once, by its LAST entry in the file.
      - xfail counts as passed (an expected failure is the outcome we wanted).
      - Errors in setup or collection count as broken.
      - flaky: an earlier entry failed and the last one passed (only possible with retries).
      - A missing file means no tests ran: return all zeros rather than crashing.
    """
    counts = {"total": 0, "passed": 0, "failed": 0, "broken": 0, "skipped": 0, "flaky": 0}
    if not junit_path.exists():
        return counts

    final_outcome = {}
    had_failed_attempt = set()
    for case in ET.parse(junit_path).getroot().iter("testcase"):
        test_id = f"{case.get('classname')}::{case.get('name')}"
        outcome = _outcome(case)
        if outcome in ("failed", "broken"):
            had_failed_attempt.add(test_id)
        final_outcome[test_id] = outcome  # a later entry overwrites an earlier attempt

    for test_id, outcome in final_outcome.items():
        counts["total"] += 1
        counts[outcome] += 1
        if outcome == "passed" and test_id in had_failed_attempt:
            counts["flaky"] += 1
    return counts


def build_status(tests: dict, env: os._Environ | dict) -> dict:
    layers = {
        "lint": env.get("LINT_RESULT", "unknown"),
        "smoke": env.get("SMOKE_RESULT", "unknown"),
    }
    overall = "passed" if all(result == "success" for result in layers.values()) else "failed"

    repo_url = f"{env.get('GITHUB_SERVER_URL', 'https://github.com')}/{env.get('GITHUB_REPOSITORY', '')}"
    sha = env.get("GITHUB_SHA", "")
    run_id = env.get("GITHUB_RUN_ID", "")

    return {
        "schema": 1,
        "project": env.get("GITHUB_REPOSITORY", "unknown/unknown").split("/")[1],
        "overall": overall,
        "generatedAt": datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z"),
        "trigger": env.get("GITHUB_EVENT_NAME", "unknown"),
        "branch": env.get("GITHUB_REF_NAME", "unknown"),
        "commit": {"sha": sha, "short": sha[:7], "url": f"{repo_url}/commit/{sha}"},
        "run": {"id": run_id, "url": f"{repo_url}/actions/runs/{run_id}"},
        "layers": layers,
        "tests": tests,
        # report is relative to this project's own Pages root. No trends page, so that key is omitted.
        "links": {"report": "report/", "testHealth": None},
    }


def main() -> None:
    if len(sys.argv) != 3:
        sys.exit("Usage: python scripts/build_status.py <junit-xml> <output-file>")
    junit_path, output_file = Path(sys.argv[1]), Path(sys.argv[2])

    status = build_status(count_tests(junit_path), os.environ)

    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(json.dumps(status, indent=2) + "\n")


if __name__ == "__main__":
    main()
