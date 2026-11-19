# Part 1B: Initial Generation Evidence Manifest

> [!WARNING]
> **Audit Notice (2026-11-20)**: The semantic quality scores recorded in `eval-results.json` and `harness-log.md` are **INVALID** due to an evaluation accounting defect where provider errors (HTTP 502 / 404 on `llama-3.3-70b-versatile`) were mistakenly counted in the confusion matrix. The files in this folder are preserved unedited for historical traceability. The ratified model `openai/gpt-oss-120b` and corrected evaluation runner are evaluated in `evidence/final-generation/`.

This directory stores the raw evaluation output and execution logs from the initial baseline benchmark run of the AI Code Review Assistant.

## Planned Deliverables (Phase 6 - T047)

1. `eval-results.json`:
   - Raw model responses for each test case in `evals/dataset.json`.
   - Per-case evaluation outputs from schema, property, and semantic evaluators.
   - Aggregated metrics across all dimensions:
     - Schema adherence score (%)
     - Deterministic invariant compliance score (%)
     - Precision (%)
     - Recall (%)
     - F1 score (%)
     - False-positive rate (%)
     - Latency statistics (p50, p95)
   - Benchmark configuration and model ID (`llama-3.3-70b-versatile`).

2. `harness-log.md`:
   - Formatted human-readable execution transcript of the baseline evaluation.
   - Verification against frozen acceptance thresholds in `evals/config.json`.
   - Identified failure patterns and prompt weaknesses informing prompt optimization (T048).

*Privacy & Security Note: In accordance with the project constitution, raw evaluation evidence will never expose API credentials, secrets, or complete submitted source code snippets.*
