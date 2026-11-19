# Part 1B: Evaluation Harness Manifest

This directory is designated for the automated evaluation harness runner and metric evaluators for Part 1B.

## Planned Deliverables (Phase 6 - T042 to T046)

1. `schema_evaluator.py`: Validates strict JSON syntax and Pydantic v2 schema adherence (100% target).
2. `property_evaluator.py`: Validates deterministic structural invariants (line number bounds, severity-action alignment, finding uniqueness).
3. `semantic_evaluator.py`: Computes precision, recall, F1, and false-positive rate against ground-truth labels.
4. `runner.py`: Orchestrates multi-case evaluation against Groq API, aggregates metrics, checks frozen thresholds, and emits JSON evidence.
5. `run-evals.sh`: Shell runner script executing the evaluation harness in the `.venv313` Python environment.

*Implementation Note: Evaluator unit tests (`tests/unit/test_eval_metrics.py`, `tests/unit/test_eval_runner.py`) will be written and confirmed failing (T042, T043) before the evaluators and runner are implemented (T044, T045).*
