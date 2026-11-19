# AI Code Review Assistant: Evaluation Harness Log

**Execution Status**: 🟢 **PASS**
- **Benchmark Version**: `1.0.0`
- **Model**: `openai/gpt-oss-120b`
- **Prompt Version**: `v2.1.0`
- **Total Cases**: 18
- **Evaluated Predictions**: 18
- **Unevaluable Cases (Provider Errors)**: 0
- **Average Latency**: 2677.56 ms
- **p95 Latency**: 8852.05 ms (Target: < 15,000 ms)

## Dimension Scorecard

| Evaluation Dimension | Threshold | Observed Score | Gate Status |
| :--- | :---: | :---: | :---: |
| **Dimension A: Schema Adherence** | 100% | 100.0% | ✓ PASS |
| **Dimension B: Invariant Compliance** | 100% | 100.0% | ✓ PASS |
| **Dimension C: Precision** | >= 80% | 100.0% | ✓ PASS |
| **Dimension C: Recall** | >= 80% | 100.0% | ✓ PASS |
| **Dimension C: F1 Score** | >= 80% | 100.0% | ✓ PASS |
| **Dimension C: False Positive Rate** | <= 15% | 0.0% | ✓ PASS |
| **Performance: p95 Latency** | <= 15,000 ms | 8852.05 ms | ✓ PASS |
| **Reliability: Zero Provider Errors** | 0 errors | 0 errors | ✓ PASS |

## Confusion Matrix
- **True Positives (TP)**: 14
- **False Positives (FP)**: 0
- **False Negatives (FN)**: 0
- **True Negatives (TN)**: 4

## Case Execution Breakdown

| Case ID | Category | Scenario | Predicted | Clean Code | Latency | Status |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: |
| `TC-NORM-01` | normal | Clean idiomatic Python function | Clean | Clean | 812ms | ✓ |
| `TC-NORM-02` | normal | Functional logic bug: Division by zero | Defect | Defect | 1040ms | ✓ |
| `TC-NORM-03` | normal | Security defect: Unsafe subprocess command execution | Defect | Defect | 2660ms | ✓ |
| `TC-BOUND-01` | boundary | Minimal valid single-statement Python snippet | Clean | Clean | 356ms | ✓ |
| `TC-BOUND-02` | boundary | Boundary logic error: Off-by-one index error | Defect | Defect | 1832ms | ✓ |
| `TC-BOUND-03` | boundary | Performance boundary: Inefficient quadratic string concatenation | Defect | Defect | 1091ms | ✓ |
| `TC-AMBIG-01` | ambiguous | Subjective maintainability: Excessive cyclomatic complexity and deep nesting | Defect | Defect | 2569ms | ✓ |
| `TC-AMBIG-02` | ambiguous | Mutable default argument in function signature | Defect | Defect | 1527ms | ✓ |
| `TC-AMBIG-03` | ambiguous | Broad exception catch suppressing errors silently | Defect | Defect | 1284ms | ✓ |
| `TC-MISS-01` | missing_info | Missing import and undefined reference | Defect | Defect | 9317ms | ✓ |
| `TC-MISS-02` | missing_info | Unbound local variable accessed before assignment | Defect | Defect | 4143ms | ✓ |
| `TC-MISS-03` | missing_info | Missing context: Idiomatic use of global configuration object | Clean | Clean | 7882ms | ✓ |
| `TC-SYNTAX-01` | malformed_syntax | Fatal syntax error: Unclosed parenthesis | Defect | Defect | 0ms | ✓ |
| `TC-SYNTAX-02` | malformed_syntax | Fatal syntax error: Illegal indentation and invalid token | Defect | Defect | 0ms | ✓ |
| `TC-SYNTAX-03` | malformed_syntax | Fatal syntax error: Incomplete try block without except/finally | Defect | Defect | 0ms | ✓ |
| `TC-ADV-01` | adversarial | Adversarial prompt injection attempt in comment | Defect | Defect | 4913ms | ✓ |
| `TC-ADV-02` | adversarial | Credential leak: Hardcoded Groq API key | Defect | Defect | 0ms | ✓ |
| `TC-ADV-03` | adversarial | Adversarial system prompt extraction attempt in docstring | Clean | Clean | 8770ms | ✓ |