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

PASS = '<testcase classname="t" name="{}" />'
FAIL = '<testcase classname="t" name="{}"><failure message="x">trace</failure></testcase>'
ERROR = '<testcase classname="t" name="{}"><error message="setup">trace</error></testcase>'
SKIP = '<testcase classname="t" name="{}"><skipped type="pytest.skip" message="no" /></testcase>'
XFAIL = '<testcase classname="t" name="{}"><skipped type="pytest.xfail" message="" /></testcase>'


@pytest.fixture
def junit(tmp_path):
    def write(*cases):
        path = tmp_path / "junit.xml"
        path.write_text(f'<testsuites><testsuite name="pytest">{"".join(cases)}</testsuite></testsuites>')
        return path

    return write


def test_counts_each_outcome(junit):
    path = junit(PASS.format("a"), FAIL.format("b"), ERROR.format("c"), SKIP.format("d"))
    assert count_tests(path) == {**NO_TESTS, "total": 4, "passed": 1, "failed": 1, "broken": 1, "skipped": 1}


def test_xfail_counts_as_passed_not_skipped(junit):
    assert count_tests(junit(XFAIL.format("a"))) == {**NO_TESTS, "total": 1, "passed": 1}


def test_retry_that_passes_is_passed_and_flaky(junit):
    path = junit(FAIL.format("a"), PASS.format("a"))
    assert count_tests(path) == {**NO_TESTS, "total": 1, "passed": 1, "flaky": 1}


def test_retry_that_keeps_failing_is_one_failure(junit):
    path = junit(FAIL.format("a"), FAIL.format("a"))
    assert count_tests(path) == {**NO_TESTS, "total": 1, "failed": 1}


def test_pass_then_teardown_error_is_broken(junit):
    path = junit(PASS.format("a"), ERROR.format("a"))
    assert count_tests(path) == {**NO_TESTS, "total": 1, "broken": 1}


def test_same_name_in_different_classes_is_two_tests(junit):
    other = PASS.format("a").replace('classname="t"', 'classname="u"')
    assert count_tests(junit(PASS.format("a"), other))["total"] == 2


def test_missing_file_counts_nothing(tmp_path):
    assert count_tests(tmp_path / "nope.xml") == NO_TESTS


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


def test_main_writes_json(junit, tmp_path, monkeypatch):
    for key, value in ENV.items():
        monkeypatch.setenv(key, value)
    out = tmp_path / "nested" / "status.json"
    monkeypatch.setattr(sys, "argv", ["build_status.py", str(junit(PASS.format("a"))), str(out)])
    build_status.main()
    written = json.loads(out.read_text())
    assert written["tests"]["passed"] == 1
    assert written["overall"] == "passed"
