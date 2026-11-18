# Deterministic Harness Validation Log

**Project**: Expense Management System (Part 1A MVP)  
**Environment**: macOS (Darwin), Python 3.9.6, Virtualenv (`.venv`)  
**Evidence Location**: `specs/001-expense-management/harness-log.md`  

---

## 1. Tooling Versions & Validation Configuration

- **Python**: `Python 3.9.6`
- **Pytest**: `pytest 8.4.2` (plugins: `anyio-4.12.1`, `asyncio-1.2.0`)
- **Ruff**: `ruff 0.17.5`
- **Bandit**: `bandit 1.8.6`
- **pip-audit**: `pip-audit 2.9.0`
- **Configuration File**: `pyproject.toml`
- **Dependency Manifest**: `requirements.txt`

---

## 2. Baseline Harness Execution (Initial Run)

### 2.1. Pytest (Unit, Integration, and Contract Tests)
- **Command**: `.venv/bin/pytest -v`
- **Initial Raw Output**:
```text
============================= test session starts ==============================
platform darwin -- Python 3.9.6, pytest-8.4.2, pluggy-1.6.0 -- /Volumes/MAC_SSD/AI_SDLC_Assignment/.venv/bin/python3
cachedir: .pytest_cache
rootdir: /Volumes/MAC_SSD/AI_SDLC_Assignment
configfile: pyproject.toml
testpaths: tests
plugins: anyio-4.12.1, asyncio-1.2.0
asyncio: mode=auto, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collecting ... collected 8 items

tests/contract/test_submit_contract.py::test_submit_expense_contract PASSED [ 12%]
tests/integration/test_expense_submit.py::test_submit_valid_expense_success PASSED [ 25%]
tests/integration/test_expense_submit.py::test_submit_negative_amount_fails FAILED [ 37%]
tests/integration/test_expense_submit.py::test_submit_zero_amount_fails FAILED [ 50%]
tests/integration/test_expense_submit.py::test_submit_more_than_two_decimals_fails FAILED [ 62%]
tests/integration/test_expense_submit.py::test_submit_future_date_fails FAILED [ 75%]
tests/integration/test_expense_submit.py::test_submit_invalid_category_fails PASSED [ 87%]
tests/integration/test_expense_submit.py::test_submit_missing_auth_headers_fails PASSED [100%]

=================================== FAILURES ===================================
...
TypeError: Object of type ValueError is not JSON serializable (in validation_exception_handler)
=================== 4 failed, 4 passed, 5 warnings in 0.57s ====================
```

### 2.2. Ruff Linter & Formatter
- **Command**: `.venv/bin/ruff check .`
- **Initial Raw Output**:
```text
F401 [*] `collections.abc.Generator` imported but unused
 --> src/api/deps.py:1:29

W293 [*] Blank line contains whitespace
  --> src/api/errors.py:42:1

E501 Line too long (103 > 100)
  --> src/api/v1/expenses.py:68:101

F401 [*] `decimal.Decimal` imported but unused
 --> src/services/expense_service.py:2:21

F541 [*] f-string without any placeholders
   --> src/services/expense_service.py:112:40

F541 [*] f-string without any placeholders
   --> src/services/expense_service.py:170:40

F401 [*] `pytest` imported but unused
 --> tests/integration/test_expense_approval.py:1:8

F401 [*] `pytest` imported but unused
 --> tests/integration/test_expense_history.py:2:8

Found 17 errors.
[*] 8 fixable with `--fix` (5 unsafe fixes available with `--fix --unsafe-fixes`).
```

### 2.3. Bandit SAST Security Scan
- **Command**: `.venv/bin/bandit -c pyproject.toml -r src/`
- **Initial Raw Output**:
```text
[main]	INFO	profile include tests: None
[main]	INFO	profile exclude tests: B101
[main]	INFO	cli include tests: None
[main]	INFO	cli exclude tests: None
[main]	INFO	using config: pyproject.toml
[main]	INFO	running on Python 3.9.6
Run started:2026-11-18 16:00:01.773361

Test results:
	No issues identified.

Code scanned:
	Total lines of code: 666
	Total lines skipped (#nosec): 0
	Total potential issues skipped due to specifically being disabled (e.g., #nosec BXXX): 0

Run metrics:
	Total issues (by severity):
		Undefined: 0
		Low: 0
		Medium: 0
		High: 0
	Total issues (by confidence):
		Undefined: 0
		Low: 0
		Medium: 0
		High: 0
Files skipped (0):
```

### 2.4. pip-audit Dependency Vulnerability Scan
- **Command**: `.venv/bin/pip-audit -r requirements.txt`
- **Initial Raw Output**:
```text
Found 21 known vulnerabilities in 8 packages
Name          Version ID                  Fix Versions
------------- ------- ------------------- ------------
starlette     0.49.3  PYSEC-2026-161      1.0.1
starlette     0.49.3  PYSEC-2026-249      1.3.1
starlette     0.49.3  PYSEC-2026-248      1.3.0
starlette     0.49.3  PYSEC-2026-2281     1.1.0
starlette     0.49.3  PYSEC-2026-2280     1.1.0
anyio         4.12.1  PYSEC-2026-4025     4.14.2
anyio         4.12.1  PYSEC-2026-4024     4.14.2
pytest        8.4.2   PYSEC-2026-1845     9.0.3
msgpack       1.1.2   PYSEC-2026-3625     1.2.1
msgpack       1.1.2   GHSA-j586-36cw-2gc2 1.2.3
filelock      3.19.1  PYSEC-2026-1375     3.20.1
filelock      3.19.1  PYSEC-2026-1374     3.20.3
filelock      3.19.1  GHSA-8mx5-7m5m-r77g 4.2.1
filelock      3.19.1  GHSA-69hj-f68j-2879 4.2.1
python-dotenv 1.2.1   PYSEC-2026-2270     1.2.2
requests      2.32.5  PYSEC-2026-2275     2.33.0
urllib3       2.6.3   PYSEC-2026-142      2.7.0
urllib3       2.6.3   PYSEC-2026-141      2.7.0
urllib3       2.6.3   PYSEC-2026-4177     2.8.0
urllib3       2.6.3   PYSEC-2026-4176     2.8.0
urllib3       2.6.3   PYSEC-2026-4175     2.8.0
```

---

## 3. Baseline Failure Evidence & Student Observations (T038)

<!-- 
================================================================================
INSTRUCTIONS FOR STUDENT:
Record your own observations, root-cause analyses, and failure classifications 
based on the raw scanner outputs above. Do NOT fabricate or delete real outputs.
================================================================================
-->

### 3.1. Pytest Failures Analysis

**Observations**

When I first ran the tests, 8 tests were executed. 4 passed and 4 failed. The failing tests were the ones that checked for negative amounts, zero amounts, more than two decimal places, and future dates.

**Root cause analysis**

The application did notice that these inputs were invalid, so the validation itself was working. The problem was in the error handler. It tried to send the error details back as a JSON response, but the details included a ValueError object, and that object could not be converted into JSON. Because of this, the response failed instead of returning a clear error message.

**Fix and result**

The error handler was updated to use jsonable_encoder and to clean up the exception context, so that only JSON-friendly values were left in the error details. After this change, the final test run in the Python 3.13.9 environment passed all 28 tests.

### 3.2. Ruff Linting Failures Analysis

**Observations**

When I first ran Ruff on the code, it reported 17 linting errors. Ruff said 8 of the issues could be fixed using `--fix`, while 5 unsafe fixes were available by enabling `--unsafe-fixes`. The problems it found were unused imports (`F401`), whitespace on blank lines (`W293`), lines that were too long (`E501`), and f-strings that had no placeholders inside them (`F541`).

**Why these issues matter**

Unused imports add clutter and make it harder to see which libraries the code really depends on. Inconsistent formatting and stray whitespace make the code harder to read and create noisy differences when several people work on the same files. Long lines are hard to read, especially on smaller screens or side-by-side comparisons. These issues don’t necessarily stop the application from running, but they can cause the quality gate to fail, so fixing them keeps the code clean and easier to maintain.

**Fix and result**

The code was cleaned up to remove the issues Ruff reported: the unused imports, the extra whitespace, the long lines, and the unnecessary f-string prefixes. After the cleanup, I ran the final checks in the Python 3.13.9 environment. `ruff check .` reported that all checks passed, and `ruff format --check .` reported that 47 files were already formatted.

### 3.3. Bandit SAST Security Scan Findings

**Observations**

When I first ran the Bandit security scan, it checked 666 lines of source code. It reported 0 high severity issues, 0 medium severity issues, 0 low severity issues, and 0 confidence issues. In other words, the baseline scan found nothing to flag.

**Why this result matters**

Bandit is a static security analysis tool, which means it reads the code without running it and looks for common security mistakes. A clean result is a good sign because it shows Bandit did not identify any risky patterns covered by its configured checks. However, it doesn’t prove the application is free of security vulnerabilities. Bandit only covers the checks it is configured to run, so other kinds of problems, such as flaws in the application’s logic, could still exist and would need other types of testing.

**Final disposition**

I ran the scan again in the Python 3.13.9 environment, and it again reported zero issues, this time across 656 lines. Since no findings were raised in either scan, no fixes were needed for this section.

### 3.4. pip-audit Dependency Vulnerability Findings

**Observations**

When I first ran pip-audit, it reported 21 vulnerability advisories across 8 packages. pip-audit checks the installed dependencies against databases of known vulnerabilities, so this result meant the original environment contained package versions with publicly known security issues.

**Why this result matters**

Applications rely on many third-party packages, and a known vulnerability in any of them can affect the application even if the project’s own code is secure. Checking dependencies helps catch these risks early, before they reach a deployed system.

**Final disposition**

I ran pip-audit again in the Python 3.13.9 environment, and it reported no known vulnerabilities. The baseline and final environments used different resolved dependency versions, so the final result reflects the versions installed in that environment. I did not individually verify how each of the 21 advisories was resolved. Also, a clean pip-audit result only means no known vulnerabilities were found at the time of the scan, and new advisories may be published later.

---

## 4. Repairs Applied & Re-Validation Gate Executions (T039)

### 4.1. Applied Codebase & Tooling Repairs
1. **Pydantic v2 Exception Serialization**: Wrapped validation error dictionaries in `src/api/errors.py` using `jsonable_encoder` and sanitized non-serializable exception objects in context dictionaries.
2. **Ruff Linting**: Cleaned up unused imports in `src/api/deps.py`, `src/services/expense_service.py`, and test files; split long lines in `src/api/v1/expenses.py`; removed unused f-string prefixes; ran automated code formatting.
3. **Tooling Configuration**: Updated `pyproject.toml` to configure Python 3.9 compatibility ignore rules for type annotation upgrades.

### 4.2. Rerun of Validation Gates (Python 3.13.9 Re-Validation)

> [!NOTE]
> **Environment Distinction**: The original baseline execution (Section 2) was captured under Python 3.9.6 in `.venv`. The final validation gates documented below were executed in an updated environment running **Python 3.13.9** in `.venv313`. The two environments did not have identical dependency versions: the Python 3.13.9 environment freshly resolved package versions from `requirements.txt`. The final `pip-audit` result applies strictly to the dependencies resolved and installed in that Python 3.13.9 environment. The original pip-audit advisories from Python 3.9.6 are preserved above as baseline historical evidence, and no claim is made that individual advisories were patched or investigated separately.

#### Gate 1: Ruff Linter & Formatter Check
- **Commands**:
  - `.venv313/bin/ruff check .`
  - `.venv313/bin/ruff format --check .`
- **Results**:
  - Ruff lint: All checks passed
  - Ruff format: 47 files already formatted
- **Raw Output**:
```text
=== RUFF LINT ===
All checks passed!
=== RUFF FORMAT ===
47 files already formatted
```

#### Gate 2: Bandit SAST Scan
- **Command**: `.venv313/bin/bandit -c pyproject.toml -r src/`
- **Result**: 656 lines scanned, zero findings at all severity and confidence levels
- **Raw Output**:
```text
[main]	INFO	profile include tests: None
[main]	INFO	profile exclude tests: B101
[main]	INFO	cli include tests: None
[main]	INFO	cli exclude tests: None
[main]	INFO	using config: pyproject.toml
[main]	INFO	running on Python 3.13.9
Run started:2026-11-18 16:22:44.841265+00:00

Test results:
	No issues identified.

Code scanned:
	Total lines of code: 656
	Total lines skipped (#nosec): 0
	Total potential issues skipped due to specifically being disabled (e.g., #nosec BXXX): 0

Run metrics:
	Total issues (by severity):
		Undefined: 0
		Low: 0
		Medium: 0
		High: 0
	Total issues (by confidence):
		Undefined: 0
		Low: 0
		Medium: 0
		High: 0
Files skipped (0):
```

#### Gate 3: pip-audit Dependency Vulnerability Scan
- **Command**: `.venv313/bin/pip-audit -r requirements.txt`
- **Result**: No known vulnerabilities found (applies to the dependency resolution under Python 3.13.9)
- **Raw Output**:
```text
No known vulnerabilities found
```

#### Gate 4: Pytest Suite (Unit, Integration, Contract)
- **Command**: `.venv313/bin/pytest -v`
- **Result**: 28 passed, 9 warnings (0 failures)
- **Warnings Record (Non-Failure Deprecation Notices)**:
  - **Startup Configuration Warning (Emitted pre-session; not included in summary count)**:
    - `PytestDeprecationWarning` in `pytest_asyncio/plugin.py:306`: The configuration option `asyncio_default_fixture_loop_scope` is unset (informational configuration notice emitted before test session starts; future versions will default to "function" scope).
  - **Pytest Session Warnings Summary (9 Starlette deprecation warnings in summary)**:
    - 1 warning in `fastapi/testclient.py:1`: `StarletteDeprecationWarning: Using 'httpx' with 'starlette.testclient' is deprecated; install 'httpx2' instead.`
    - 8 warnings across `test_expense_approval.py` (2), `test_expense_submit.py` (5), and `test_quickstart.py` (1) in `starlette/_exception_handler.py:59`: `StarletteDeprecationWarning: 'HTTP_422_UNPROCESSABLE_ENTITY' is deprecated. Use 'HTTP_422_UNPROCESSABLE_CONTENT' instead.`
  - *(Note: The nine warnings reported in the pytest session summary are all Starlette deprecation warnings. The pytest-asyncio configuration warning is emitted at startup before the test session and is not counted in the session total. None of these represent test failures; all 28 test cases passed.)*
- **Raw Output**:
```text
/Volumes/MAC_SSD/AI_SDLC_Assignment/.venv313/lib/python3.13/site-packages/pytest_asyncio/plugin.py:306: PytestDeprecationWarning: The configuration option "asyncio_default_fixture_loop_scope" is unset.
The event loop scope for asynchronous fixtures will default to the fixture scope. Future versions of pytest-asyncio will default the loop scope for asynchronous fixtures to "function" scope. Set the default fixture loop scope explicitly in order to avoid unexpected behavior in the future. Valid fixture loop scopes are: "function", "class", "module", "package", "session". Set it to "fixture-scope" to keep the current behavior.

  warnings.warn(PytestDeprecationWarning(_DEFAULT_FIXTURE_LOOP_SCOPE_UNSET))
============================= test session starts ==============================
platform darwin -- Python 3.13.9, pytest-9.2.0, pluggy-1.7.0 -- /Volumes/MAC_SSD/AI_SDLC_Assignment/.venv313/bin/python
cachedir: .pytest_cache
rootdir: /Volumes/MAC_SSD/AI_SDLC_Assignment
configfile: pyproject.toml
testpaths: tests
plugins: platformdirs-4.14.7, anyio-4.16.0, asyncio-1.5.0
asyncio: mode=Mode.AUTO, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collecting ... collected 28 items

tests/contract/test_approval_contract.py::test_approve_expense_contract PASSED [  3%]
tests/contract/test_approval_contract.py::test_reject_expense_contract PASSED [  7%]
tests/contract/test_history_contract.py::test_list_expenses_contract PASSED [ 10%]
tests/contract/test_history_contract.py::test_get_expense_detail_contract PASSED [ 14%]
tests/contract/test_submit_contract.py::test_submit_expense_contract PASSED [ 17%]
tests/integration/test_expense_approval.py::test_manager_approve_expense_success PASSED [ 21%]
tests/integration/test_expense_approval.py::test_manager_reject_expense_success PASSED [ 25%]
tests/integration/test_expense_approval.py::test_manager_reject_missing_or_short_reason_fails PASSED [ 28%]
tests/integration/test_expense_approval.py::test_employee_cannot_approve_or_reject PASSED [ 32%]
tests/integration/test_expense_approval.py::test_manager_self_approval_prohibited PASSED [ 35%]
tests/integration/test_expense_approval.py::test_terminal_state_locking PASSED [ 39%]
tests/integration/test_expense_approval.py::test_approve_reject_nonexistent_expense PASSED [ 42%]
tests/integration/test_expense_history.py::test_employee_sees_only_own_expenses PASSED [ 46%]
tests/integration/test_expense_history.py::test_manager_sees_all_submitted_expenses PASSED [ 50%]
tests/integration/test_expense_history.py::test_filter_expenses_by_status PASSED [ 53%]
tests/integration/test_expense_history.py::test_filter_expenses_by_category_and_date PASSED [ 57%]
tests/integration/test_expense_history.py::test_employee_cannot_view_other_employee_detail PASSED [ 60%]
tests/integration/test_expense_history.py::test_get_nonexistent_expense_detail PASSED [ 64%]
tests/integration/test_expense_submit.py::test_submit_valid_expense_success PASSED [ 67%]
tests/integration/test_expense_submit.py::test_submit_negative_amount_fails PASSED [ 71%]
tests/integration/test_expense_submit.py::test_submit_zero_amount_fails PASSED [ 75%]
tests/integration/test_expense_submit.py::test_submit_more_than_two_decimals_fails PASSED [ 78%]
tests/integration/test_expense_submit.py::test_submit_future_date_fails PASSED [ 82%]
tests/integration/test_expense_submit.py::test_submit_invalid_category_fails PASSED [ 85%]
tests/integration/test_expense_submit.py::test_submit_missing_auth_headers_fails PASSED [ 89%]
tests/integration/test_quickstart.py::test_quickstart_scenario_a_employee_submit PASSED [ 92%]
tests/integration/test_quickstart.py::test_quickstart_scenario_b_negative_validation_and_self_approval PASSED [ 96%]
tests/integration/test_quickstart.py::test_quickstart_scenario_c_rejection_and_immutability PASSED [100%]

=============================== warnings summary ===============================
.venv313/lib/python3.13/site-packages/fastapi/testclient.py:1
  /Volumes/MAC_SSD/AI_SDLC_Assignment/.venv313/lib/python3.13/site-packages/fastapi/testclient.py:1: StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
    from starlette.testclient import TestClient as TestClient  # noqa

tests/integration/test_expense_approval.py::test_manager_reject_missing_or_short_reason_fails
tests/integration/test_expense_approval.py::test_manager_reject_missing_or_short_reason_fails
tests/integration/test_expense_submit.py::test_submit_negative_amount_fails
tests/integration/test_expense_submit.py::test_submit_zero_amount_fails
tests/integration/test_expense_submit.py::test_submit_more_than_two_decimals_fails
tests/integration/test_expense_submit.py::test_submit_future_date_fails
tests/integration/test_expense_submit.py::test_submit_invalid_category_fails
tests/integration/test_quickstart.py::test_quickstart_scenario_b_negative_validation_and_self_approval
  /Volumes/MAC_SSD/AI_SDLC_Assignment/.venv313/lib/python3.13/site-packages/starlette/_exception_handler.py:59: StarletteDeprecationWarning: 'HTTP_422_UNPROCESSABLE_ENTITY' is deprecated. Use 'HTTP_422_UNPROCESSABLE_CONTENT' instead.
    response = await handler(conn, exc)  # type: ignore[arg-type]

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
======================== 28 passed, 9 warnings in 0.19s ========================
```

---

## 5. Final Validation Evidence & Security Disposition (T040)

<!-- 
================================================================================
INSTRUCTIONS FOR STUDENT:
Document your final conclusions below based on the actual scanner evidence above.
Verify:
1. Passing unit, integration, and contract tests (28 passed).
2. Successful Ruff checks (all passed).
3. Bandit findings with severity and disposition (0 findings).
4. pip-audit findings with affected dependencies and disposition (categorize dev vs runtime risks).
5. State of unresolved blocking security findings.
================================================================================
-->

### 5.1. Test Suite Verification

### Final test execution

I ran the full test suite in the Python 3.13 virtual environment. Pytest reported 28 passed, 0 failed, and 9 warnings, finishing in 0.20 seconds. This is a clear improvement over the first run, where 4 of 8 tests failed.

### Test coverage

The 28 tests fall into three groups:

- Contract tests (5): check that the API endpoints accept and return the expected requests and responses.
- Integration tests (20): check expense submission, approval, rejection, history and validation working together.
- Quickstart tests (3): run complete example workflows from start to finish.

Together they cover employee expense submission, manager approval and rejection, rejection reason validation, employee permission limits, prevention of manager self-approval, locking of finished expenses, filtering by status, category and date, and missing authentication headers. They also cover the input rules that failed earlier: negative amounts, zero amounts, more than two decimal places, future dates and invalid categories. These tests check both what the application does and the business rules it must follow.

### Warnings observed

There were two kinds of warnings, and none of them caused a test to fail.

1. Pytest-asyncio configuration warning: the asyncio_default_fixture_loop_scope option is not set explicitly, and the library warns that its default behaviour will change in a future version.
2. Starlette deprecation warnings (9 in the summary): one says that using HTTPX with starlette.testclient is deprecated, and eight say that HTTP_422_UNPROCESSABLE_ENTITY is deprecated in favour of HTTP_422_UNPROCESSABLE_CONTENT.

These are deprecation and configuration notices, not errors. They should still be treated as technical debt to clean up later, since future library versions could change this behaviour.

### Final assessment

All 28 implemented tests passed with no failures, so the test suite meets the acceptance criteria. This shows the implemented test cases pass. It does not prove that every possible scenario works, and the warnings are noted for future maintenance.

### 5.2. Code Quality & Static Check Verification

### Initial code quality findings

The first Ruff scan reported 17 linting errors. These included unused imports (F401), whitespace on blank lines (W293), lines over the length limit (E501), and f-strings without placeholders (F541).

### Repairs and improvements

The code was cleaned up to address each of these: unused imports were removed, extra whitespace was cleared, long lines were fixed, and unnecessary f-string prefixes were dropped.

### Final lint and formatting results

In the Python 3.13.9 environment, ruff check . reported that all checks passed. ruff format --check . reported that all 47 files were already formatted, and the --check flag means it verified this without changing any files.

### Final assessment

The source code now meets the configured lint and formatting rules, which makes it easier to read, review and maintain. However, Ruff passing does not mean the application is free from runtime bugs or security vulnerabilities. Those are covered by the test suite and the security tools.

### 5.3. Bandit SAST Disposition

### Final Bandit scan results

I ran the final scan in the Python 3.13.9 environment with `.venv313/bin/bandit -c pyproject.toml -r src/`. It scanned 656 lines of source code, and no files were skipped.

### Severity and confidence assessment

Bandit reported 0 high, 0 medium and 0 low severity findings, and 0 confidence findings. The baseline scan of 666 lines also reported zero findings.

### Remediation disposition

Because neither scan raised any findings, no Bandit-specific remediation was necessary.

### Security limitations and final assessment

Bandit did not identify any security issues covered by its configured checks in the scanned source code. However, static analysis cannot guarantee complete security. It cannot detect every vulnerability, especially business-logic, configuration, deployment or runtime problems, so this result is one part of the overall assessment.

### 5.4. pip-audit Dependency Vulnerability Disposition

### Baseline dependency findings

The baseline pip-audit scan, run in the Python 3.9.6 environment, reported 21 vulnerability advisories across 8 packages: Starlette 0.49.3, AnyIO 4.12.1, Pytest 8.4.2, Msgpack 1.1.2, Filelock 3.19.1, python-dotenv 1.2.1, Requests 2.32.5 and urllib3 2.6.3.

### Runtime and development dependency risk

Starlette, AnyIO and python-dotenv have confirmed links to the application’s runtime stack (FastAPI, Pydantic Settings and Uvicorn). Pytest, Msgpack, Filelock, Requests and urllib3 appear linked to testing and audit tooling, such as CacheControl and pip-audit. This is a preliminary classification, not proof that they are only development dependencies.

### Final dependency audit results

In the Python 3.13.9 environment, `.venv313/bin/pip-audit -r requirements.txt` reported no known vulnerabilities.

### Remediation and environment differences

The two environments differed. The final one was freshly resolved from `requirements.txt`, which uses minimum version constraints, so newer package versions could be installed. The clean result reflects that new dependency set, not individual fixes.

### Limitations and final assessment

I did not individually verify how each of the 21 baseline advisories was resolved. The clean scan means no known vulnerabilities were found at the time of scanning. It does not prove complete application security, and new advisories may appear later.

### 5.5. Human Security Verification and Acceptance

### Verification details

- Application: Expense Management System
- Final environment: Python 3.13.9
- Verification date: 19th November 2026
- Reviewer: Prashant Bhattacharya

### Validation summary

- Test suite: 28 passed, 0 failed, 9 warnings (deprecation and configuration notices only)
- Ruff lint and formatting: `ruff check .` passed, and `ruff format --check .` reported 47 files already formatted
- Bandit SAST: no issues identified across 656 lines of source code, with zero findings at every severity level (high, medium, low) and every confidence level
- pip-audit: no known vulnerabilities in the final environment. The baseline had 21 advisories across 8 packages, and I did not individually verify how each one was resolved.
- Manual application verification: Completed

### Blocking security findings assessment

The validation activities I performed identified no unresolved blocking security findings. Bandit reported nothing in either scan, and the final pip-audit scan reported no known vulnerabilities. These results are limited to what the tools check. Bandit cannot detect business-logic, configuration or runtime problems. pip-audit only reflects advisories known at the time of the scan, and new ones may appear later. The final dependency set was freshly resolved and differs from the baseline environment. The test suite shows that the 28 implemented cases pass, not that every scenario works.

### Final acceptance decision

ACCEPT

### Justification

All 28 tests passed, the Ruff lint and formatting checks passed, Bandit reported zero findings, and the final pip-audit scan reported no known vulnerabilities. I manually verified that the application starts, that employees can submit expenses, and that managers can approve and reject them. The rule that employees cannot approve their own expenses is covered by the automated tests. Rejected expenses cannot be changed later because the application has no update or delete endpoints for them, and the automated tests also cover this locked state. On this evidence, I accept the implementation. I note that automated scans cannot guarantee complete security, and that dependency advisories should be rechecked periodically.

### Student sign-off

- Name: Prashant Bhattacharya
- Signature: Prashant Bhattacharya
- Date: 19th November 2026
