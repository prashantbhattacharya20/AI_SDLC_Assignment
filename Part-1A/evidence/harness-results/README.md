# Part 1A: Harness Results Manifest

This directory preserves raw scanner and test execution outputs produced by the deterministic validation harness.

## Preserved Raw Evidence Files

- **`python313-rerun-evidence.txt`**: Complete, unedited terminal capture from the final validation rerun under Python 3.13.9 (`.venv313`) covering:
  - `pytest -v` (28 passed, 9 Starlette deprecation warnings in 0.19s)
  - `ruff check .` (All checks passed!)
  - `ruff format --check .` (47 files already formatted)
  - `bandit -c pyproject.toml -r src/` (656 lines scanned, 0 issues identified)
  - `pip-audit -r requirements.txt` (No known vulnerabilities found)

## Evidence Lineage

A matching canonical copy of `python313-rerun-evidence.txt` is also maintained at `Part-1A/specs/001-expense-management/python313-rerun-evidence.txt` to preserve original Spec Kit artifact linkage.
