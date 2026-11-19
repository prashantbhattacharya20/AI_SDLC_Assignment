# Part 1B: Evaluation Benchmark Manifest

This directory is designated for the ground-truth evaluation dataset and benchmark configuration for the AI Code Review Assistant.

## Planned Deliverables (Phase 6 - T040 & T041)

1. `config.json`: Frozen metric thresholds and benchmark parameters:
   - Schema Adherence: 100%
   - Deterministic Invariant Compliance: 100%
   - Precision: $\ge 80\%$
   - Recall: $\ge 80\%$
   - F1 Score: $\ge 80\%$
   - False-Positive Rate: $\le 15\%$

2. `dataset.json`: Ground-truth evaluation dataset containing at least 15 verified test cases spanning all 6 required categories:
   - Clean / Idiomatic Python code
   - Logic / Functional bugs
   - Security vulnerabilities (OWASP / Bandit)
   - Performance / Algorithmic inefficiencies
   - Maintainability / Complexity smells
   - Deterministic boundary / Syntax error cases

*Implementation Note: These artifacts will be populated during Phase 6 execution according to tasks T040 and T041 in `tasks.md` prior to running the baseline benchmark.*
