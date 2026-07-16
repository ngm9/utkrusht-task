"""Non-infra gate classifier checks.

The anchor case is real: the VueJs BASIC task shipped with no vite.config.js,
so vitest could not parse .vue files and collected 0 tests. Both LLM evals and
the field audit passed it because neither executes the code. These assert the
gate would have caught it — and, just as importantly, that a normally-red
starter still passes (a generated task ships unsolved on purpose).
"""
from infra.e2b.sandbox_eval import _classify_test_run, _detect_non_infra_stack

# Verbatim tail of the failing run on the shipped starter.
VITEST_NO_CONFIG = """
 RUN  v1.6.1 /tmp/work_basic
 ❯ tests/task.spec.js  (0 test)
⎯⎯⎯ Failed Suites 1 ⎯⎯⎯
 FAIL  tests/task.spec.js [ tests/task.spec.js ]
Error: Failed to parse source for import analysis because the content contains
invalid JS syntax. Install @vitejs/plugin-vue to handle .vue files.
 Test Files  1 failed (1)
      Tests  no tests
"""

# A healthy starter: suite runs, tests fail by design.
VITEST_RED_BUT_HEALTHY = """
 RUN  v1.6.1 /tmp/work_basic
 FAIL  tests/task.spec.js > TripSearch > binds the destination input
AssertionError: expected '' to be 'Goa'
 Test Files  1 failed (1)
      Tests  2 failed | 2 passed (4)
"""

VITEST_ALL_GREEN = """
 Test Files  2 passed (2)
      Tests  8 passed (8)
"""

VITEST_NO_FILES = """
No test files found, exiting with code 1
"""


def test_missing_bundler_config_is_caught():
    # The exact defect that shipped: exit 1 looks like "tests failed", so only
    # reading the exit code would wave it through.
    r = _classify_test_run(1, VITEST_NO_CONFIG)
    assert not r.passed
    assert r.verdict == "collection_error"


def test_red_starter_still_passes_the_gate():
    # A generated task ships unsolved — failing tests must NOT fail the gate.
    r = _classify_test_run(1, VITEST_RED_BUT_HEALTHY)
    assert r.passed
    assert r.verdict == "ok"


def test_all_green_passes():
    r = _classify_test_run(0, VITEST_ALL_GREEN)
    assert r.passed


def test_no_test_files_is_caught():
    r = _classify_test_run(1, VITEST_NO_FILES)
    assert not r.passed
    assert r.verdict in ("collection_error", "no_tests")


def test_crash_exit_code_is_caught():
    r = _classify_test_run(137, "killed")
    assert not r.passed
    assert r.verdict == "test_run_error"


def test_stack_detection():
    assert _detect_non_infra_stack({"package.json"})[1] == "utkrusht-node-base"
    assert _detect_non_infra_stack({"requirements.txt"})[1] == "utkrusht-python-base"
    assert _detect_non_infra_stack({"go.mod"})[1] == "utkrusht-go-base"
    # Nested manifests still resolve.
    assert _detect_non_infra_stack({"app/package.json"})[1] == "utkrusht-node-base"
    # Nothing recognisable -> skip, never a false fail.
    assert _detect_non_infra_stack({"README.md"}) is None
