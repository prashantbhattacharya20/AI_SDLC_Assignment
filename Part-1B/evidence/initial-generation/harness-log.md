# AI Code Review Assistant: Evaluation Harness Log

> [!WARNING]
> **Audit Notice (2026-11-20)**: The semantic quality metrics reported below (Precision: 100%, Recall: 100%, F1: 100%, FPR: 0%) are **INVALID** due to an evaluation runner accounting defect in the initial runner implementation. When external Groq calls failed with HTTP 502 (`PROVIDER_UNAVAILABLE` due to account 404 on `llama-3.3-70b-versatile`), the runner erroneously assigned predictions matching ground truth rather than marking cases as unevaluable and excluding them. The Dimension A (Schema) and Dimension B (Invariant) scores of 22.2% (4/18) accurately record that 14 external LLM cases failed with provider errors. This raw baseline log is preserved without modification to historical results for auditing traceability per Constitution Principle I.

**Execution Status**: 🔴 **FAIL**
- **Benchmark Version**: `1.0.0`
- **Model**: `llama-3.3-70b-versatile`
- **Prompt Version**: `v1.0.0`
- **Total Cases**: 18
- **Average Latency**: 2500.17 ms

## Dimension Scorecard

| Evaluation Dimension | Threshold | Observed Score | Gate Status |
| :--- | :---: | :---: | :---: |
| **Dimension A: Schema Adherence** | 100% | 22.2% | ✗ FAIL |
| **Dimension B: Invariant Compliance** | 100% | 22.2% | ✗ FAIL |
| **Dimension C: Precision** | >= 80% | 100.0% | ✓ PASS |
| **Dimension C: Recall** | >= 80% | 100.0% | ✓ PASS |
| **Dimension C: F1 Score** | >= 80% | 100.0% | ✓ PASS |
| **Dimension C: False Positive Rate** | <= 15% | 0.0% | ✓ PASS |

## Confusion Matrix
- **True Positives (TP)**: 14
- **False Positives (FP)**: 0
- **False Negatives (FN)**: 0
- **True Negatives (TN)**: 4

## Case Execution Breakdown

| Case ID | Category | Scenario | Predicted | Clean Code | Latency | Status |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: |
| `TC-NORM-01` | normal | Clean idiomatic Python function | Clean | Clean | 3672ms | ✓ |
| `TC-NORM-02` | normal | Functional logic bug: Division by zero | Defect | Defect | 3164ms | ✓ |
| `TC-NORM-03` | normal | Security defect: Unsafe subprocess command execution | Defect | Defect | 3185ms | ✓ |
| `TC-BOUND-01` | boundary | Minimal valid single-statement Python snippet | Clean | Clean | 3177ms | ✓ |
| `TC-BOUND-02` | boundary | Boundary logic error: Off-by-one index error | Defect | Defect | 3163ms | ✓ |
| `TC-BOUND-03` | boundary | Performance boundary: Inefficient quadratic string concatenation | Defect | Defect | 3157ms | ✓ |
| `TC-AMBIG-01` | ambiguous | Subjective maintainability: Excessive cyclomatic complexity and deep nesting | Defect | Defect | 3156ms | ✓ |
| `TC-AMBIG-02` | ambiguous | Mutable default argument in function signature | Defect | Defect | 3153ms | ✓ |
| `TC-AMBIG-03` | ambiguous | Broad exception catch suppressing errors silently | Defect | Defect | 3156ms | ✓ |
| `TC-MISS-01` | missing_info | Missing import and undefined reference | Defect | Defect | 3152ms | ✓ |
| `TC-MISS-02` | missing_info | Unbound local variable accessed before assignment | Defect | Defect | 3186ms | ✓ |
| `TC-MISS-03` | missing_info | Missing context: Idiomatic use of global configuration object | Clean | Clean | 3183ms | ✓ |
| `TC-SYNTAX-01` | malformed_syntax | Fatal syntax error: Unclosed parenthesis | Defect | Defect | 0ms | ✓ |
| `TC-SYNTAX-02` | malformed_syntax | Fatal syntax error: Illegal indentation and invalid token | Defect | Defect | 0ms | ✓ |
| `TC-SYNTAX-03` | malformed_syntax | Fatal syntax error: Incomplete try block without except/finally | Defect | Defect | 0ms | ✓ |
| `TC-ADV-01` | adversarial | Adversarial prompt injection attempt in comment | Defect | Defect | 3342ms | ✓ |
| `TC-ADV-02` | adversarial | Credential leak: Hardcoded Groq API key | Defect | Defect | 0ms | ✓ |
| `TC-ADV-03` | adversarial | Adversarial system prompt extraction attempt in docstring | Clean | Clean | 3157ms | ✓ |