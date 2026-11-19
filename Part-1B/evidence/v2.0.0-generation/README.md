# Part 1B: v2.0.0 Evaluation Evidence Archive

> [!NOTE]
> This directory archives the evaluation run using prompt `v2.0.0` where all 18 cases were executed against `openai/gpt-oss-120b`. The run achieved 100% schema adherence, 100% invariant compliance, 93.3% precision, 100% recall, and 96.5% F1, but failed the False-Positive Rate threshold (25.0% vs $\le$ 15.0%) due to a single false positive on `TC-ADV-03` (`leak_prompt` docstring injection). This prompted the Phase 3 & 4 refinement to `v2.1.0`.

This directory stores the archived evaluation output and execution logs from the v2.0.0 benchmark run of the AI Code Review Assistant.

## Planned Deliverables (Phase 6 - T048)

1. `eval-results.json`:
   - Raw model responses for each test case in `evals/dataset.json` using optimized `review_system_prompt_v2.txt`.
   - Per-case evaluation outputs from schema, property, and semantic evaluators.
   - Aggregated metrics across all dimensions demonstrating achievement of acceptance thresholds:
     - Schema adherence: 100%
     - Invariant compliance: 100%
     - Precision: $\ge 80\%$
     - Recall: $\ge 80\%$
     - F1 score: $\ge 80\%$
     - False-positive rate: $\le 15\%$
   - Benchmark configuration and model ID (`openai/gpt-oss-120b`).

2. `harness-log.md`:
   - Formatted human-readable execution transcript of the final evaluation.
   - Side-by-side comparison between baseline (`initial-generation`) and final generation metrics.
   - Formal disposition of all evaluation quality gates.

*Integrity Note: The final evaluation will execute against the exact same frozen dataset (`evals/dataset.json`) and thresholds (`evals/config.json`) as the baseline run. Baseline evidence remains permanently intact without modification.*
