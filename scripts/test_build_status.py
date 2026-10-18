import json
import sys

import pytest

import build_status
from build_status import build_status as make_status
from build_status import count_tests

ENV = {
    "GITHUB_REPOSITORY": "owner/some-repo",
    "GITHUB_SHA": "0123456789abcdef0123456789abcdef01234567",
    "GITHUB_RUN_ID": "42",
    "GITHUB_EVENT_NAME": "schedule",
    "GITHUB_REF_NAME": "main",
    "LINT_RESULT": "success",
    "SMOKE_RESULT": "success",
}
NO_TESTS = {"total": 0, "passed": 0, "failed": 0, "broken": 0, "skipped": 0, "flaky": 0}

@pytest.fixture
def results(tmp_path):
    """Write one Allure result file per call. Calls with the same name are attempts of the same test."""
    counter = iter(range(1000))

    def write(name, status, stop=None, message=None):
        n = next(counter)
        result = {"name": name, "historyId": f"id-{name}", "status": status, "stop": stop if stop is not None else n}
        if message:
            result["statusDetails"] = {"message": message}
        (tmp_path / f"{n}-result.json").write_text(json.dumps(result))
        return tmp_path

    return write


def test_counts_each_outcome(results):
    results("a", "passed")
    results("b", "failed")
    results("c", "broken")
    path = results("d", "skipped")
    assert count_tests(path) == {**NO_TESTS, "total": 4, "passed": 1, "failed": 1, "broken": 1, "skipped": 1}


def test_xfail_counts_as_passed_not_skipped(results):
    path = results("a", "skipped", message="XFAIL  AssertionError: assert False")
    assert count_tests(path) == {**NO_TESTS, "total": 1, "passed": 1}


def test_a_normal_skip_stays_skipped(results):
    path = results("a", "skipped", message="Skipped: no browser")
    assert count_tests(path) == {**NO_TESTS, "total": 1, "skipped": 1}


def test_xpass_counts_as_passed(results):
    assert count_tests(results("a", "passed", message="XPASS")) == {**NO_TESTS, "total": 1, "passed": 1}


def test_retry_that_passes_is_passed_and_flaky(results):
    results("a", "failed")
    path = results("a", "passed")
    assert count_tests(path) == {**NO_TESTS, "total": 1, "passed": 1, "flaky": 1}


def test_retry_that_keeps_failing_is_one_failure(results):
    results("a", "failed")
    path = results("a", "failed")
    assert count_tests(path) == {**NO_TESTS, "total": 1, "failed": 1}


def test_last_attempt_is_chosen_by_stop_time_not_file_order(results):
    results("a", "passed", stop=200)
    path = results("a", "failed", stop=100)  # written later, but it ran earlier
    assert count_tests(path) == {**NO_TESTS, "total": 1, "passed": 1, "flaky": 1}


def test_pass_then_a_later_failure_is_failed(results):
    results("a", "passed", stop=100)
    path = results("a", "failed", stop=200)
    assert count_tests(path) == {**NO_TESTS, "total": 1, "failed": 1}


def test_unreadable_status_is_never_counted_as_a_pass(results):
    assert count_tests(results("a", "unknown")) == {**NO_TESTS, "total": 1, "broken": 1}


def test_other_files_in_the_folder_are_ignored(results):
    path = results("a", "passed")
    (path / "environment.properties").write_text("Browser=chrome\n")
    (path / "x-container.json").write_text("{}")
    (path / "x-attachment.json").write_text("{}")
    assert count_tests(path) == {**NO_TESTS, "total": 1, "passed": 1}


def test_missing_folder_counts_nothing(tmp_path):
    assert count_tests(tmp_path / "nope") == NO_TESTS


def test_status_passes_only_when_every_layer_succeeds():
    assert make_status(NO_TESTS, ENV)["overall"] == "passed"
    assert make_status(NO_TESTS, {**ENV, "SMOKE_RESULT": "failure"})["overall"] == "failed"
    assert make_status(NO_TESTS, {**ENV, "LINT_RESULT": "skipped"})["overall"] == "failed"


def test_status_matches_the_contract():
    status = make_status(NO_TESTS, ENV)
    assert status["schema"] == 1
    assert status["project"] == "some-repo"
    assert status["trigger"] == "schedule"
    assert status["commit"]["short"] == "0123456"
    assert status["commit"]["url"] == "https://github.com/owner/some-repo/commit/" + ENV["GITHUB_SHA"]
    assert status["run"]["url"] == "https://github.com/owner/some-repo/actions/runs/42"
    assert status["layers"] == {"lint": "success", "smoke": "success"}
    assert status["links"] == {"report": "report/awesome/", "trends": "report/dashboard/", "testHealth": None}
    assert status["generatedAt"].endswith("Z")


def test_main_writes_json(results, tmp_path, monkeypatch):
    for key, value in ENV.items():
        monkeypatch.setenv(key, value)
    out = tmp_path / "nested" / "status.json"
    monkeypatch.setattr(sys, "argv", ["build_status.py", str(results("a", "passed")), str(out)])
    build_status.main()
    written = json.loads(out.read_text())
    assert written["tests"]["passed"] == 1
    assert written["overall"] == "passed"
