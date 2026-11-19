# Data Model: AI Code Review Assistant

**Feature**: `001-code-review-assistant`<br>
**Date**: 2026-11-20<br>
**Status**: Completed (Reviewed & Revised)<br>

---

## 1. Domain Enumerations

### 1.1 `DefectCategory` (Enum: str)
Represents the standardized taxonomy of defect classifications:
- `BUG`: Functional defects, logical flaws, unhandled exceptions, incorrect edge-case logic.
- `SECURITY`: Security vulnerabilities, unvalidated inputs, injection flaws, OWASP antipatterns.
- `PERFORMANCE`: Algorithmic inefficiencies, redundant computation, excessive memory allocations.
- `MAINTAINABILITY`: Code smells, cognitive complexity, duplicate patterns, anti-idiomatic structures.

### 1.2 `SeverityLevel` (Enum: str)
Represents the triage priority and severity ranking:
- `CRITICAL`: High-impact defects, fatal syntax errors, remote exploit vulnerabilities, severe data loss risks.
- `HIGH`: Major functional bugs, significant security flaws, memory leaks, high-frequency performance bottlenecks.
- `MEDIUM`: Moderate edge-case bugs, sub-optimal algorithms, missing input guards.
- `LOW`: Minor code smells, non-idiomatic patterns, minor refactoring opportunities.
- `INFO`: Informational suggestions, stylistic improvements, documentation comments.

### 1.3 `ReviewStatus` (Enum: str)
Represents the aggregate release quality gate decision:
- `FAIL`: Indicated when `critical_count > 0` or `high_count > 0`.
- `PASS`: Indicated when `critical_count == 0` and `high_count == 0` (even if medium/low/info findings exist).

---

## 2. Core Data Entities & Schemas

### 2.1 `CodeReviewRequest`
Payload submitted by clients to request static code analysis:

| Field | Type | Required | Default | Validation & Constraints |
|-------|------|----------|---------|--------------------------|
| `code` | `str` | Yes | - | Non-empty string; stripped length > 0; maximum 1,000 lines; maximum 65,536 UTF-8 bytes. Exceeding either limit triggers HTTP 413 (`PAYLOAD_TOO_LARGE`). |
| `file_path` | `Optional[str]` | No | `None` | Optional file path or module identifier (e.g., `services/auth.py`). |
| `language` | `str` | No | `"python"` | Target programming language. Strictly `"python"` for MVP. Any other value is rejected with HTTP 422 (`UNSUPPORTED_LANGUAGE`). |
| `include_markdown` | `bool` | No | `False` | When `True`, system generates a formatted markdown report string in the response. |

### 2.2 `ReviewFinding`
Represents an individual discrete defect identified during review:

| Field | Type | Required | Validation & Invariant Rules |
|-------|------|----------|------------------------------|
| `id` | `str` | Yes | Unique finding identifier (e.g., `finding-001` or UUID). |
| `title` | `str` | Yes | Concise defect summary; non-empty, max 120 characters. |
| `category` | `DefectCategory` | Yes | Must match one of `BUG`, `SECURITY`, `PERFORMANCE`, `MAINTAINABILITY`. |
| `severity` | `SeverityLevel` | Yes | Must match one of `CRITICAL`, `HIGH`, `MEDIUM`, `LOW`, `INFO`. |
| `start_line` | `int` | Yes | Positive integer `>= 1`; must be `<= total_source_lines`. |
| `end_line` | `int` | Yes | Positive integer `>= start_line`; must be `<= total_source_lines`. |
| `description` | `str` | Yes | Detailed technical explanation of the identified issue; non-empty string. |
| `recommendation` | `str` | Yes | Actionable remediation guidance; non-empty string. |
| `confidence` | `float` | Yes | Model-reported subjective certainty estimate bounded between `0.0` and `1.0`. *Note: This is a self-assessed estimate, not a calibrated statistical probability. All deterministic schema and invariant checks remain completely independent of this score.* |

### 2.3 `ReviewSummary`
Aggregate metrics and gate decision for a review execution:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `status` | `ReviewStatus` | Yes | `FAIL` if `critical_count + high_count > 0`, else `PASS`. |
| `total_findings` | `int` | Yes | Sum of all detected discrete findings. |
| `critical_count` | `int` | Yes | Count of findings with severity `CRITICAL`. |
| `high_count` | `int` | Yes | Count of findings with severity `HIGH`. |
| `medium_count` | `int` | Yes | Count of findings with severity `MEDIUM`. |
| `low_count` | `int` | Yes | Count of findings with severity `LOW`. |
| `info_count` | `int` | Yes | Count of findings with severity `INFO`. |

### 2.4 `ReviewTelemetry`
Observability metrics recording operational metadata:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `model_id` | `str` | Yes | Exact configured LLM identifier (`openai/gpt-oss-120b`, or `deterministic-ast` when handled locally). |
| `prompt_version` | `str` | Yes | Version identifier of the prompt template (e.g., `v1.0.0`). |
| `latency_ms` | `float` | Yes | Total execution latency in milliseconds. |
| `prompt_tokens` | `Optional[int]` | No | Input tokens consumed (if provided by LLM API; `null` for local AST runs). |
| `completion_tokens` | `Optional[int]` | No | Output tokens generated (if provided by LLM API; `null` for local AST runs). |
| `total_tokens` | `Optional[int]` | No | Total tokens billed (if provided by LLM API; `null` for local AST runs). |
| `retry_count` | `int` | Yes | Number of retries executed after initial attempt (bounded between `0` and `2`). |

### 2.5 `CodeReviewResult`
The complete structured API response payload:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `review_id` | `str` | Yes | Unique UUID for the review execution. |
| `timestamp` | `datetime` | Yes | UTC timestamp of review execution (ISO-8601). |
| `file_path` | `Optional[str]` | No | Preserved from request (nullable). |
| `language` | `str` | Yes | Language evaluated (`"python"`). |
| `summary` | `ReviewSummary` | Yes | Aggregate counts and overall gate status. |
| `findings` | `List[ReviewFinding]` | Yes | Validated, deduplicated list of findings. |
| `telemetry` | `ReviewTelemetry` | Yes | Execution observability metrics. |
| `markdown_report` | `Optional[str]` | No | Formatted Markdown summary (populated if requested; nullable). |

### 2.6 `ErrorResponse`
Standardized error structure returned on client and server errors:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `error_code` | `str` | Yes | Machine-readable error code (`SECRET_DETECTED`, `UNSUPPORTED_LANGUAGE`, `PAYLOAD_TOO_LARGE`, `VALIDATION_ERROR`, `PROVIDER_ERROR`). |
| `message` | `str` | Yes | Human-readable diagnostic explanation without leaking secrets or provider internals. |
| `details` | `Optional[Dict[str, Any]]` | No | Optional structured diagnostic details (nullable). |

---

## 3. Deterministic Invariant Rules

Every instance of `CodeReviewResult` and its child models MUST satisfy the following invariant rules before being returned:
1. **Source Bounds Invariant**: For every finding, `1 <= start_line <= end_line <= total_lines_in_source`.
2. **Field Non-Emptiness Invariant**: `title`, `description`, and `recommendation` must not be empty or whitespace-only.
3. **Deduplication Invariant**: No two findings in `findings` may share the same `(category, start_line, end_line, description)`. If duplicate entries occur, the engine retains only one instance.
4. **Summary Consistency Invariant**: `total_findings == len(findings) == (critical_count + high_count + medium_count + low_count + info_count)`.
5. **Quality Gate Consistency Invariant**: `status == ReviewStatus.FAIL` if and only if `(critical_count + high_count) > 0`.
6. **Independence from Confidence**: Invariant validation is unconditional; findings are not exempted or modified based on the model's reported `confidence` score.
