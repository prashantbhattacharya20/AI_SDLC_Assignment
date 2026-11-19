# Phase 0 Research: AI Code Review Assistant

**Feature**: `001-code-review-assistant`<br>
**Date**: 2026-11-20<br>
**Status**: Completed (Reviewed & Revised)<br>

---

## 1. LLM Provider Integration & Client Abstraction

- **Decision**: Integrate exclusively with the Groq Python SDK (`groq` package) isolated behind a clean `LLMClient` protocol/interface. Standardize on `openai/gpt-oss-120b` (hosted on Groq LPUs) as the single model for the MVP and all evaluation benchmarks (ratified on 2026-11-20 to replace initial planning placeholder `llama-3.3-70b-versatile`, which is unavailable/HTTP 404 on the Groq account tier). Remove all alternative or fallback model designations (such as `llama-3.1-8b-instant`). The exact configured model ID (`openai/gpt-oss-120b`, or `deterministic-ast` when handled locally) MUST be recorded in execution telemetry.
- **Rationale**:
  - `openai/gpt-oss-120b` provides high-parameter code reasoning, strict instruction adherence, native JSON mode (`response_format={"type": "json_object"}`), sub-second inference on Groq, and active availability on the provisioned Groq account.
  - Using a single standardized model ensures consistent, reproducible evaluation benchmarks across initial and final prompt iterations.
  - A clean abstraction layer isolates model invocation logic so test suites inject deterministic mocks without modifying application workflow.
- **Alternatives Considered**:
  - *llama-3.3-70b-versatile*: Initial candidate; unavailable on provisioned Groq account (returns HTTP 404 model_not_found).
  - *Fallback to smaller models (llama-3.1-8b-instant)*: Rejected; multiple models introduce evaluation confounding factors and variable schema compliance for the MVP. Also unavailable on account tier.
  - *Direct HTTP calls via httpx*: Viable but adds redundant boilerplate for authentication, streaming, and error mapping already handled cleanly by the official `groq` SDK.
  - *Multi-provider orchestration frameworks (LangChain, LlamaIndex, LiteLLM)*: Rejected per Constitution Principle II (Avoid premature abstractions and unnecessary dependencies). Scoped exclusively to Groq for Part 1B.

---

## 2. Language Handling & Pre-Validation Pipeline

- **Decision**: Explicitly restrict MVP scope to Python (`python`) as the only supported programming language.
  - Any request specifying an unsupported language (or non-Python file extension when inferred) MUST be rejected upfront with an HTTP 422 Unprocessable Entity error (error code: `UNSUPPORTED_LANGUAGE`).
  - Python AST parsing MUST NEVER be executed against source code identified as an unsupported language.
  - Validation order is strictly enforced:
    1. Language verification (must be `"python"`).
    2. Payload limits verification (line count and byte length).
    3. Secret screening (detecting and rejecting credential signatures).
    4. Deterministic AST syntax parsing (for Python source).
    5. External LLM invocation (only if previous checks pass).
- **Rationale**:
  - Clarifies language boundaries and prevents invalid parser exceptions from running Python tools against non-Python syntax.
  - Returns clear, actionable client errors before initiating expensive processing.
- **Alternatives Considered**:
  - *Multi-language support in MVP*: Rejected; increases prompt complexity and benchmark surface area beyond assignment requirements.

---

## 3. Payload Limits & Size Constraints

- **Decision**: Enforce dual payload ceilings:
  - Maximum line count: **1,000 lines**.
  - Maximum payload size: **65,536 UTF-8 bytes (64 KB)**.
  - Exceeding either limit MUST immediately produce an **HTTP 413 Payload Too Large** response (error code: `PAYLOAD_TOO_LARGE`).
- **Rationale**:
  - Unifies previous discrepancies between character counts and byte lengths to standard UTF-8 byte measurement.
  - Prevents Denial-of-Service (DoS) risks, excessive memory consumption, and context window overflow.
  - Maps to the semantically correct HTTP 413 status code rather than general validation errors (HTTP 422).
- **Alternatives Considered**:
  - *Character count instead of UTF-8 byte count*: Multi-byte unicode characters can bypass character limits while expanding memory footprint; byte length is the standard network and storage measure.

---

## 4. Secret Detection & Pre-Transmission Screening

- **Decision**: Implement a deterministic pattern-matching screening engine (`SecretScanner`) utilizing pre-compiled regular expressions covering common credential formats:
  - Groq API keys (`gsk_[a-zA-Z0-9]{48}`)
  - OpenAI / Anthropic keys (`sk-[a-zA-Z0-9]{32,}`, `sk-ant-[a-zA-Z0-9]{32,}`)
  - GitHub Personal Access Tokens (`ghp_[a-zA-Z0-9]{36}`)
  - AWS Access Key IDs (`AKIA[0-9A-Z]{16}`)
  - Generic Private Keys (`-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----`)
  - Generic password/token assignments in source (`(?:api[_-]?key|secret|password|token)\s*=\s*['"][^'"]+['"]`)
  - *Action on Match*: Immediately reject the submission with an **HTTP 422 Unprocessable Entity** error (error code: `SECRET_DETECTED`) identifying the matched pattern name without echoing the sensitive substring.
- **Rationale**:
  - Satisfies ratified clarification Q1 and Constitution Principle IV.
  - Prevents proprietary credentials from being transmitted to external cloud LLM APIs.
  - Pattern matching executes in sub-millisecond time locally with zero external network dependencies.
- **Alternatives Considered**:
  - *External scanning libraries (detect-secrets, trufflehog)*: Heavy dependencies with large rule databases unnecessary for single-file source review scope.
  - *In-place secret masking/redaction*: Rejected during clarification Q1 in favor of strict immediate rejection to enforce developer security hygiene.

---

## 5. Deterministic AST Syntax Verification

- **Decision**: Execute Python standard library `ast.parse()` on submitted Python code prior to dispatching external LLM requests. If a `SyntaxError` occurs, intercept the exception immediately, construct a valid `CodeReviewResult` containing a single `CRITICAL` severity `BUG` finding with the exact line number, column offset, and syntax error text, and return HTTP 200 without calling Groq.
- **Rationale**:
  - Satisfies ratified clarification Q2.
  - Broken syntax cannot be executed; asking an LLM to review code that fails basic parsing wastes API quota, incurs unnecessary latency, and risks hallucinatory advice.
  - Using Python's built-in `ast` module guarantees 100% language fidelity without third-party dependencies.
- **Alternatives Considered**:
  - *Rejecting syntax errors with HTTP 422*: Rejected during clarification Q2; developers expect code reviewers to point out syntax bugs within normal review reports.
  - *Passing broken code to LLM*: Increases cost and latency with lower accuracy than the compiler's own parser.

---

## 6. Bounded Resilience, Retry Policy & Error Mapping

- **Decision**: Implement a bounded retry strategy for external Groq model calls:
  - Maximum **two retries** after the initial attempt (up to 3 total attempts).
  - Exponential backoff: approximately **1 second** after attempt 1, and **2 seconds** after attempt 2 (with small random jitter to avoid thundering herd).
  - **Retryable Conditions**:
    - Transient network timeouts and connection drops (`groq.APIConnectionError`, `groq.APITimeoutError`).
    - Upstream rate limits (`groq.RateLimitError` / HTTP 429).
    - Recoverable malformed JSON or schema validation parse failures from the model output.
  - **Non-Retryable Conditions**:
    - Authentication failures (`groq.AuthenticationError` / HTTP 401).
    - Permission/authorization failures (`groq.PermissionDeniedError` / HTTP 403).
    - Invalid request configuration or unrecoverable client errors.
    - *Action on Non-Retryable Failure*: Fail immediately without retrying.
  - **Exhausted Failure Handling**: If all retries are exhausted, the service MUST return an **HTTP 502 Bad Gateway** error (error code: `PROVIDER_ERROR`).
  - **Privacy Rule**: Raw exception traces, API keys, and sensitive provider internals MUST NEVER be exposed in client responses or standard logs.
- **Rationale**:
  - Provides resilience against intermittent cloud network blips while bounding maximum execution time.
  - Differentiates external provider failures (HTTP 502) from internal application crashes (HTTP 500) or client request errors (HTTP 4xx).

---

## 7. Performance Targets & Reproducible Measurement

- **Decision**: Maintain target response latencies:
  - **< 15 seconds** for submissions under 500 lines.
  - **< 30 seconds** for submissions up to the 1,000-line limit.
- **Measurement Method & Conditions**:
  - Targets represent **p95 latency** measured end-to-end from HTTP request receipt to HTTP response serialization.
  - Test conditions: warm service instance, standard broadband internet connectivity (RTT < 100ms to Groq API gateway), measured over a sample of at least 20 consecutive benchmark runs on typical code complexity.
  - *Important Qualification*: These figures represent empirical targets under normal operating conditions and standard provider availability, rather than unconditional contractual SLA guarantees.

---

## 8. Finding Confidence Semantics

- **Decision**: Define the `confidence` field (float `0.0` to `1.0`) in `ReviewFinding` as a model-reported subjective estimate of self-assessed certainty, rather than a calibrated statistical probability.
- **Independence of Invariants**: Deterministic schema validation, line range verification, deduplication, and quality gate calculations (`PASS`/`FAIL`) operate completely independently of the confidence score. Every finding, regardless of confidence value, must strictly satisfy all schema invariants.

---

## 9. Automated Testing & Evaluation Harness Architecture

- **Decision**: Separate deterministic testing from empirical LLM evaluation:
  1. *CI Test Suite (`tests/`)*: 100% deterministic, offline, and fast. All external Groq client interactions are mocked using Pytest fixtures. Tests verify endpoint routing, schema validation, secret screening, syntax interception, invariant checks, and error mappings.
  2. *Empirical Evaluation Harness (`.harness/` & `evals/`)*: Standalone runner (`run_evals.py`) executing against `evals/dataset.json` containing at least **15 verified cases** across six scenario categories:
     - Normal review scenarios.
     - Boundary conditions.
     - Ambiguous code/requirements.
     - Missing mandatory information.
     - Malformed/unsupported inputs.
     - Adversarial/guardrail inputs.
  3. *Three Independent Evaluation Dimensions*:
     - **Dimension A**: Structural/schema compliance (Target: 100%).
     - **Dimension B**: Deterministic invariants (Target: 100%).
     - **Dimension C**: Semantic quality (Target: Precision >= 80%, Recall >= 80%, F1 >= 80%, False Positive Rate <= 15%).
  4. Pre-established acceptance thresholds MUST be finalized before live benchmark execution; ground-truth labels and evaluation metrics MUST NEVER be fabricated.
