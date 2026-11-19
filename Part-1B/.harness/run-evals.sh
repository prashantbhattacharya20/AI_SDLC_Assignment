#!/bin/bash
set -euo pipefail

# ---------------------------------------------------------------------------
# Part 1B: Evaluation Benchmark Harness Shell Runner
# ---------------------------------------------------------------------------

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PART1B_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
REPO_ROOT="$(cd "$PART1B_DIR/.." && pwd)"

# Activate virtualenv if available
if [[ -f "$REPO_ROOT/.venv313/bin/activate" ]]; then
    # shellcheck disable=SC1091
    source "$REPO_ROOT/.venv313/bin/activate"
elif [[ -f "$REPO_ROOT/.venv/bin/activate" ]]; then
    # shellcheck disable=SC1091
    source "$REPO_ROOT/.venv/bin/activate"
fi

export PYTHONPATH="$PART1B_DIR"

MODE="${1:-baseline}"

echo "================================================================="
echo "Executing Evaluation Benchmark Harness: Part 1B ($MODE)"
echo "================================================================="

python -m evals.runner --mode "$MODE"
