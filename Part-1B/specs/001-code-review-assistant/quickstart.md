# Quickstart & Validation Guide: AI Code Review Assistant

**Feature**: `001-code-review-assistant`<br>
**Date**: 2026-11-20<br>
**Status**: Ready (Reviewed & Revised)<br>

---

## 1. Prerequisites & Environment Setup

Ensure you are working in the project root with the ratified Python 3.13.9 virtual environment:

```bash
# From repository root:
source .venv313/bin/activate

# Verify Python version:
python --version  # Must output Python 3.13.9

# Navigate to Part-1B:
cd Part-1B
```

### Environment Configuration

Configure `Part-1B/.env` (excluded by `.gitignore`):

```bash
GROQ_API_KEY=gsk_your_groq_api_key_here
GROQ_MODEL=openai/gpt-oss-120b
ENVIRONMENT=development
```

*Note: `openai/gpt-oss-120b` (hosted on Groq) is the single ratified model utilized across MVP analysis and evaluation benchmarks.*

---

## 2. Running Deterministic Tests

Per Constitution Principle I, all unit, contract, and integration tests utilize mocked provider responses and execute fully offline without requiring a live Groq API key:

```bash
# Run complete test suite:
pytest -v

# Run contract compliance tests (validating OpenAPI 3.1 schemas):
pytest tests/contract/ -v

# Run secret screening & AST pre-validation unit tests:
pytest tests/unit/ -v

# Run end-to-end mocked API integration tests:
pytest tests/integration/ -v
```

---

## 3. Starting the Local FastAPI Service

```bash
# Launch Uvicorn server:
uvicorn src.main:app --host 127.0.0.1 --port 8000 --reload
```

Interactive OpenAPI documentation is available at `http://127.0.0.1:8000/docs`.

---

## 4. End-to-End Validation Scenarios

### Scenario 1: Healthcheck Verification

```bash
curl -s http://127.0.0.1:8000/api/v1/health | jq .
```
**Expected Outcome**:
```json
{
  "status": "ok",
  "provider": "groq",
  "version": "1.0.0"
}
```

---

### Scenario 2: Normal Code Review (Defect Detection)

Submit Python code containing an unvalidated SQL query:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/review \
  -H "Content-Type: application/json" \
  -d '{
    "code": "def get_user(db, username):\n    query = f\"SELECT * FROM users WHERE name = '\''{username}'\''\"\n    return db.execute(query).fetchone()",
    "file_path": "services/user_service.py",
    "language": "python",
    "include_markdown": true
  }' | jq .
```

**Expected Outcome**:
- HTTP Status `200 OK`.
- `summary.status`: `"FAIL"`.
- At least one finding under category `"SECURITY"`, severity `"HIGH"` or `"CRITICAL"`, with actionable recommendation.
- `telemetry.latency_ms` recorded with `telemetry.model_id`: `"openai/gpt-oss-120b"`.
- Finding `confidence` is a float between 0.0 and 1.0 (subjective estimate).

---

### Scenario 3: Clean Code Submission

Submit clean, idiomatic Python code without defects:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/review \
  -H "Content-Type: application/json" \
  -d '{
    "code": "def calculate_rectangle_area(width: float, height: float) -> float:\n    \"\"\"Calculate the area of a rectangle.\"\"\"\n    if width <= 0 or height <= 0:\n        raise ValueError(\"Dimensions must be positive.\")\n    return width * height",
    "file_path": "utils/geometry.py",
    "language": "python"
  }' | jq .
```

**Expected Outcome**:
- HTTP Status `200 OK`.
- `summary.status`: `"PASS"`.
- `findings`: `[]` (empty list).
- `summary.total_findings`: `0`.

---

### Scenario 4: Secret Detection Rejection (Security Hygiene)

Submit code containing an identifiable API key:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/review \
  -H "Content-Type: application/json" \
  -d '{
    "code": "GROQ_KEY = \"gsk_abcdefghijklmnopqrstuvwxyz012345678901234567890123\"\nclient = Groq(api_key=GROQ_KEY)",
    "language": "python"
  }' | jq .
```

**Expected Outcome**:
- HTTP Status `422 Unprocessable Entity`.
- Response error code: `"SECRET_DETECTED"`.
- Zero calls dispatched to external Groq API.
- The secret substring is NOT logged or echoed back.

---

### Scenario 5: Deterministic Syntax Error Interception

Submit code with unparseable Python syntax:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/review \
  -H "Content-Type: application/json" \
  -d '{
    "code": "def broken_func(:\n    print(\"Hello world\")",
    "language": "python"
  }' | jq .
```

**Expected Outcome**:
- HTTP Status `200 OK`.
- `summary.status`: `"FAIL"`.
- Single finding: `category`: `"BUG"`, `severity`: `"CRITICAL"`, line `1`, description detailing Python syntax error.
- `telemetry.model_id`: `"deterministic-ast"` (0 external LLM tokens consumed).

---

### Scenario 6: Unsupported Language Rejection

Submit code requesting an unsupported language (e.g., JavaScript):

```bash
curl -X POST http://127.0.0.1:8000/api/v1/review \
  -H "Content-Type: application/json" \
  -d '{
    "code": "console.log(\"Hello world\");",
    "language": "javascript"
  }' | jq .
```

**Expected Outcome**:
- HTTP Status `422 Unprocessable Entity`.
- Error code: `"UNSUPPORTED_LANGUAGE"`.
- Zero AST parsing or LLM calls executed.

---

### Scenario 7: Oversized Payload Rejection (Lines or Bytes)

Submit code exceeding 1,000 lines or 65,536 UTF-8 bytes:

```bash
# Generate 1,050 lines of code:
python -c 'import json; print(json.dumps({"code": "\n".join([f"x_{i} = {i}" for i in range(1050)]), "language": "python"}))' | \
curl -X POST http://127.0.0.1:8000/api/v1/review \
  -H "Content-Type: application/json" \
  -d @- | jq .
```

**Expected Outcome**:
- HTTP Status `413 Payload Too Large`.
- Error code: `"PAYLOAD_TOO_LARGE"`.

---

## 5. Running the LLM Evaluation Benchmark Harness

When validating empirical detection accuracy against the ground-truth benchmark suite:

```bash
# Ensure live GROQ_API_KEY is exported:
export GROQ_API_KEY="your-live-api-key"

# Execute evaluation harness against evals/dataset.json:
python -m evals.runner \
  --dataset evals/dataset.json \
  --output evidence/final-generation/benchmark_results.json

# View summarized metrics:
cat evidence/final-generation/benchmark_results.json | jq .metrics
```

### Benchmark Dimension Criteria & Pre-Set Thresholds:
- **Dimension A (Schema Adherence)**: 100% of responses must adhere to Pydantic/OpenAPI schema.
- **Dimension B (Deterministic Invariants)**: 100% of finding line numbers within source bounds, non-empty fields, valid deduplication.
- **Dimension C (Semantic Defect Quality)**:
  - Precision: >= 80%
  - Recall: >= 80%
  - F1 Score: >= 80%
  - False-Positive Rate: <= 15%
- *Ground-truth labels and outcomes are strictly verified; fabrication of benchmark results is prohibited.*
