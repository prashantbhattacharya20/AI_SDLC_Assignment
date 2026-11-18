# Part 1A: Initial Generation Evidence Manifest

This directory documents the initial baseline generation evidence for Part 1A (Expense Management System - MVP).

## Baseline Evidence Record

Per the project constitution and deterministic validation requirements, all initial baseline execution results were captured directly from the live harness execution and are recorded verbatim in:

- **Primary Evidence Log**: [../harness-log.md](../harness-log.md#2-baseline-harness-execution-initial-run) (Section 2: Baseline Harness Execution)
- **Environment**: Python 3.9.6, Virtualenv (`.venv`)

### Recorded Baseline Outcomes

1. **Pytest (Unit, Integration, Contract)**:
   - 8 tests executed: 4 passed, 4 failed.
   - Failures identified: Negative amount, zero amount, >2 decimal places, future date inputs.
   - Root cause: `TypeError: Object of type ValueError is not JSON serializable` in Starlette exception handler.
   - Raw output preserved in Section 2.1 of `harness-log.md`.

2. **Ruff Linter & Formatter**:
   - 17 linting errors detected across `src/` and `tests/` (`F401` unused imports, `W293` whitespace, `E501` long lines, `F541` f-strings without placeholders).
   - Raw output preserved in Section 2.2 of `harness-log.md`.

3. **Bandit SAST**:
   - 666 lines scanned, 0 issues identified at all severity and confidence levels.
   - Raw output preserved in Section 2.3 of `harness-log.md`.

4. **pip-audit SCA**:
   - 21 known vulnerability advisories detected across 8 packages (`starlette`, `anyio`, `pytest`, `msgpack`, `filelock`, `python-dotenv`, `requests`, `urllib3`).
   - Raw output preserved in Section 2.4 of `harness-log.md`.

*Note: Per assignment integrity constraints, synthetic or artificial code snapshots are not manufactured. All genuine initial evidence is preserved verbatim in the evidence log cited above.*
