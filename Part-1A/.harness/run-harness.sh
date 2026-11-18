#!/usr/bin/env bash
# ==============================================================================
# Deterministic Validation Harness Runner - Part 1A (Expense Management System)
# ==============================================================================
# Faithfully executes the four deterministic validation gates:
# Gate 1: Ruff Linter & Formatter Check
# Gate 2: Bandit SAST Scan
# Gate 3: pip-audit Dependency Vulnerability Scan
# Gate 4: Pytest Suite (Unit, Integration, Contract)
# ==============================================================================
set -euo pipefail

# Determine script and Part-1A directory locations
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PART_1A_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
REPO_ROOT="$(cd "${PART_1A_DIR}/.." && pwd)"

# Resolve Python environment: prefer root .venv313, then active VIRTUAL_ENV, then .venv
if [ -d "${REPO_ROOT}/.venv313" ]; then
    VENV_PATH="${REPO_ROOT}/.venv313"
elif [ -n "${VIRTUAL_ENV:-}" ] && [ -d "${VIRTUAL_ENV}" ]; then
    VENV_PATH="${VIRTUAL_ENV}"
elif [ -d "${REPO_ROOT}/.venv" ]; then
    VENV_PATH="${REPO_ROOT}/.venv"
else
    VENV_PATH=""
fi

if [ -n "${VENV_PATH}" ]; then
    export PATH="${VENV_PATH}/bin:${PATH}"
    echo "==> Using Python environment: ${VENV_PATH} ($(${VENV_PATH}/bin/python --version))"
fi

cd "${PART_1A_DIR}"
echo "==> Working directory: ${PART_1A_DIR}"

echo ""
echo "========================================================================"
echo "Gate 1: Ruff Linting & Formatting Check"
echo "========================================================================"
ruff check .
ruff format --check .

echo ""
echo "========================================================================"
echo "Gate 2: Bandit Static Application Security Testing (SAST)"
echo "========================================================================"
bandit -c pyproject.toml -r src/

echo ""
echo "========================================================================"
echo "Gate 3: pip-audit Dependency Vulnerability Scan"
echo "========================================================================"
pip-audit -r requirements.txt

echo ""
echo "========================================================================"
echo "Gate 4: Pytest Automated Verification Suite"
echo "========================================================================"
pytest -v

echo ""
echo "========================================================================"
echo "Harness Result: ALL GATES PASSED (100% Deterministic Verification)"
echo "========================================================================"
