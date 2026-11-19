# Part 1B: Final Generation Evidence Manifest

This directory stores the raw evaluation output and execution logs from the final live benchmark run of the AI Code Review Assistant using ratified prompt `review_system_prompt_v2_1.txt` (`v2.1.0`) and Groq-hosted `openai/gpt-oss-120b`.

## Completed Deliverables (Phase 6 - T048 & Phase 4 Revalidation)

1. `eval-results.json`:
   - Raw model responses for each of the 18 test cases in `evals/dataset.json`.
   - Aggregated metrics across all dimensions demonstrating 100% achievement of acceptance thresholds:
     - Schema adherence: 100.0% (Threshold: 100%)
     - Invariant compliance: 100.0% (Threshold: 100%)
     - Precision: 100.0% (Threshold: $\ge 80\%$)
     - Recall: 100.0% (Threshold: $\ge 80\%$)
     - F1 score: 100.0% (Threshold: $\ge 80\%$)
     - False-positive rate: 0.0% (Threshold: $\le 15\%$)
     - p95 Latency: 8,852.05 ms (Threshold: $\le 15,000$ ms)
     - Average Latency: 2,677.56 ms
     - Provider Errors: 0
   - Model ID: `openai/gpt-oss-120b` (Groq provider).

2. `harness-log.md`:
   - Formatted human-readable execution transcript of the final live evaluation.
   - Per-case breakdown across all 18 benchmark scenarios.
   - Status: 🟢 **PASS** across all dimensions.

*Historical Traceability Note: Baseline evidence in `evidence/initial-generation/` and previous intermediate v2.0.0 evidence in `evidence/v2.0.0-generation/` remain permanently intact without modification.*
