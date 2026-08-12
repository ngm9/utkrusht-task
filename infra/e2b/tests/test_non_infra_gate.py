"""Non-infra gate classifier checks.

The anchor case is real: the VueJs BASIC task shipped with no vite.config.js,
so vitest could not parse .vue files and collected 0 tests. Both LLM evals and
the field audit passed it because neither executes the code. These assert the
gate would have caught it — and, just as importantly, that a normally-red
starter still passes (a generated task ships unsolved on purpose).
"""
from infra.e2b.sandbox_eval import (
    _require_red_starter,
    _classify_dotnet,
    _classify_test_run,
    _detect_non_infra_stack,
)

# `dotnet test` exits 1 for BOTH of these — only the output separates them.
DOTNET_BUILD_ERROR = """
Determining projects to restore...
/task/src/OrderService.cs(42,17): error CS1002: ; expected
Build FAILED.
"""

DOTNET_RED_BUT_HEALTHY = """
Determining projects to restore...
Build succeeded.
  Failed OrderTotals_ApplyDiscount [12 ms]
  Error Message: Assert.Equal() Failure: Expected 90, Actual 100
Failed!  - Failed: 3, Passed: 5, Skipped: 0, Total: 8
"""

DOTNET_NO_TESTS = """
Build succeeded.
No test is available in /task/bin/Debug/net8.0/Task.dll.
"""

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


def test_dotnet_build_error_is_caught():
    # Exit 1 here means "does not compile", not "tests failed".
    r = _classify_dotnet(1, DOTNET_BUILD_ERROR)
    assert not r.passed
    assert r.verdict == "collection_error"


def test_dotnet_red_starter_still_passes_the_gate():
    # Same exit code as the build error above — the output is what separates them.
    r = _classify_dotnet(1, DOTNET_RED_BUT_HEALTHY)
    assert r.passed
    assert r.verdict == "ok"


def test_dotnet_no_tests_is_caught():
    r = _classify_dotnet(1, DOTNET_NO_TESTS)
    assert not r.passed
    assert r.verdict == "no_tests"


# Verbatim from the C# ADVANCED run: told "does not compile", the generator
# marked the 5 failing tests [Fact(Skip=...)] and the suite went green.
DOTNET_SKIPPED_TO_GREEN = (
    "Passed!  - Failed:     0, Passed:     2, Skipped:     5, Total:     7, "
    "Duration: 161 ms - TransferPosting.Tests.dll (net8.0)"
)

VITEST_ALL_PASS_NOTHING_TO_SOLVE = """
 Test Files  2 passed (2)
      Tests  8 passed (8)
"""

PYTEST_WITH_SKIPS = "3 failed, 2 passed, 4 skipped in 0.31s"

PYTEST_ZERO_SKIPPED = "3 failed, 2 passed, 0 skipped in 0.31s"


def test_skipping_tests_to_go_green_is_caught():
    # The exact regression: exit 0 + "Passed!" looks healthy, but 5 disabled
    # tests mean the required guarantees are never checked.
    r = _require_red_starter(0, DOTNET_SKIPPED_TO_GREEN)
    assert r is not None and not r.passed
    # exit 0 is itself disqualifying — nothing left to solve.
    assert r.verdict == "already_green"


def test_skipped_tests_caught_even_when_suite_is_red():
    r = _require_red_starter(1, PYTEST_WITH_SKIPS)
    assert r is not None and not r.passed
    assert r.verdict == "tests_skipped"


def test_all_green_starter_is_rejected():
    r = _require_red_starter(0, VITEST_ALL_PASS_NOTHING_TO_SOLVE)
    assert r is not None and r.verdict == "already_green"


def test_genuinely_red_starter_is_allowed_through():
    assert _require_red_starter(1, VITEST_RED_BUT_HEALTHY) is None
    assert _require_red_starter(1, DOTNET_RED_BUT_HEALTHY) is None


def test_zero_skipped_is_not_a_skip():
    # "0 skipped" must not trip the skip check.
    assert _require_red_starter(1, PYTEST_ZERO_SKIPPED) is None


def test_stack_detection():
    assert _detect_non_infra_stack({"package.json"})[1] == "utkrusht-node-base"
    assert _detect_non_infra_stack({"requirements.txt"})[1] == "utkrusht-python-base"
    assert _detect_non_infra_stack({"go.mod"})[1] == "utkrusht-go-base"
    # Nested manifests still resolve.
    assert _detect_non_infra_stack({"app/package.json"})[1] == "utkrusht-node-base"
    # C# has no fixed manifest name — match on the .csproj suffix, nested or not.
    assert _detect_non_infra_stack({"OrderService.csproj"})[1] == "utkrusht-dotnet-base"
    assert _detect_non_infra_stack({"src/Api/Api.csproj"})[3] == "dotnet test --nologo"
    # Nothing recognisable -> skip, never a false fail.
    assert _detect_non_infra_stack({"README.md"}) is None
