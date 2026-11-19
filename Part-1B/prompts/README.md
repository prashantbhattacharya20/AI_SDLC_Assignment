# Part 1B: Versioned Prompts Manifest

This directory stores versioned prompt templates utilized by the Groq LLM integration.

## Planned Deliverables

1. `review_system_prompt_v1.txt` (Phase 2 - T013):
   - Baseline system prompt instructing `openai/gpt-oss-120b` (hosted on Groq) to return findings strictly adhering to the JSON schema.
   - Evaluated during initial baseline benchmark (T047).

2. `review_system_prompt_v2.txt` (Phase 6 - T048):
   - Initial optimized system prompt addressing failure modes, hallucinations, or boundary ambiguities identified during baseline evaluation.
   - Preserved as historical evidence from the v2.0.0 benchmark evaluation.

3. `review_system_prompt_v2_1.txt` (Phase 6 - v2.1.0 Refinement):
   - Ratified refinement incorporating explicit Passive Untrusted Code Rule and Secret Identification Rule.
   - Enforces spec.md Line 80: treats adversarial prompt injection instructions in comments/docstrings as passive source data rather than code defects, preventing false positives on clean functions with adversarial docstrings (TC-ADV-03).
   - Distinguishes genuine credentials from harmless mock identifiers and placeholder strings ('sensitive_data', 'test_token').
