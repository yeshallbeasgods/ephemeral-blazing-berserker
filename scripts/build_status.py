"""Writes the status.json that the portfolio hub reads (schema 1). Run by CI after the tests:

    python scripts/build_status.py allure-results publish/status.json

Job results arrive as LINT_RESULT / SMOKE_RESULT (the values of `needs.<job>.result`).
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path


def _outcome(result: dict) -> str:
    """Map one Allure result to passed / failed / broken / skipped."""
    status = result.get("status")
    if status == "skipped" and (result.get("statusDetails") or {}).get("message", "").startswith("XFAIL"):
        return "passed"  # Allure reports an expected failure as skipped
    if status in ("passed", "failed", "broken", "skipped"):
        return status
    return "broken"  # "unknown" or a missing status: never count a result we cannot read as a pass


def count_tests(results_dir: Path) -> dict:
    """Return {"total", "passed", "failed", "broken", "skipped", "flaky"} from an allure-results folder.

    Why Allure and not the junit XML: with retries (pytest-rerunfailures) the junit file writes a retried
    attempt as an empty, passing-looking <testcase>, so a flaky test cannot be told apart from a pass.
    Allure writes one result file per attempt, all sharing a historyId.

    Rules (agreed for the shared contract):
      - Each test counts once, by its LAST attempt (latest "stop" time).
      - xfail counts as passed (an expected failure is the outcome we wanted).
      - Errors in setup or collection count as broken.
      - flaky: an earlier attempt failed (or broke) and the last one passed.
      - A missing folder means no tests ran: return all zeros rather than crashing.
    """
    counts = {"total": 0, "passed": 0, "failed": 0, "broken": 0, "skipped": 0, "flaky": 0}
    if not results_dir.is_dir():
        return counts

    last_attempt = {}  # historyId -> (stop, outcome)
    had_failed_attempt = set()
    for file in sorted(results_dir.glob("*-result.json")):
        result = json.loads(file.read_text(encoding="utf-8"))
        test_id = result.get("historyId") or file.name
        outcome = _outcome(result)
        stop = result.get("stop", 0)
        if outcome in ("failed", "broken"):
            had_failed_attempt.add(test_id)
        if test_id not in last_attempt or stop >= last_attempt[test_id][0]:
            last_attempt[test_id] = (stop, outcome)

    for test_id, (_, outcome) in last_attempt.items():
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
        # Both links are relative to this project's own Pages root.
        # report: the full Allure report. trends: charts across runs.
        "links": {"report": "report/awesome/", "trends": "report/dashboard/", "testHealth": None},
    }


def main() -> None:
    if len(sys.argv) != 3:
        sys.exit("Usage: python scripts/build_status.py <allure-results-dir> <output-file>")
    results_dir, output_file = Path(sys.argv[1]), Path(sys.argv[2])

    status = build_status(count_tests(results_dir), os.environ)

    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(json.dumps(status, indent=2) + "\n")


if __name__ == "__main__":
    main()
