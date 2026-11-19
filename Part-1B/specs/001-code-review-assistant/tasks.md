---
description: "Task list for AI Code Review Assistant implementation"
---

# Tasks: AI Code Review Assistant

**Input**: Design documents from `specs/001-code-review-assistant/`
- Specification: [spec.md](spec.md)
- Implementation Plan: [plan.md](plan.md)
- Technical Research: [research.md](research.md)
- Data Model: [data-model.md](data-model.md)
- API Contract: [contracts/code-review-api.yaml](contracts/code-review-api.yaml)
- Quickstart Guide: [quickstart.md](quickstart.md)

**Governance**: Project Constitution v1.1.1 (Strict Test-First & Eval-Driven Development; all unit, contract, and integration tests authored and observed failing before implementation; GroqClient sole owner of retry logic; empirical benchmark evaluation decoupled).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story as a discrete MVP increment.

---

## Format: `- [ ] [TaskID] [P?] [Story?] Description with file path`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete tasks)
- **[Story]**: User story identifier (`[US1]`, `[US2]`, `[US3]`) mapping directly to `spec.md`
- Exact file paths included in all task descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization, dependency management, and code quality tooling.

- [X] T001 Create project source, test, evaluation, and evidence directory structure per implementation plan in src/, tests/, evals/, .harness/, and evidence/
- [X] T002 Initialize Python 3.13.9 dependencies (FastAPI, Uvicorn, Pydantic, pydantic-settings, Groq SDK, Pytest, HTTPX, pytest-mock, Ruff, Bandit, pip-audit) in requirements.txt
- [X] T003 [P] Configure code quality and security tooling (Ruff linter/formatter, Bandit SAST configuration, Pytest testpaths) in pyproject.toml

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core application infrastructure that MUST be completed before ANY user story can be implemented.

**⚠️ CRITICAL**: Strict TDD is enforced. Shared test fixtures and failing test suites MUST be authored first, confirmed failing (Red), and then satisfied by implementation (Green).

### Tests for Foundational Prerequisites (TDD - Written & Failing First) ⚠️

- [X] T004 Create shared test fixtures (mock Groq client, sample code snippets, canned model responses) in tests/conftest.py
- [X] T005 [P] Write failing unit tests for application configuration and environment variable loading in tests/unit/test_config.py
- [X] T006 [P] Write failing unit tests for domain enumerations and error response schemas in tests/unit/test_schemas.py
- [X] T007 [P] Write failing unit tests for GroqClient and retry logic in tests/unit/test_llm_client.py, verifying retryable errors, permanent errors, backoff delay, retry count recording, and exhausted retries
- [X] T008 [P] Write failing unit tests for prompt template rendering and schema instructions in tests/unit/test_prompt_rendering.py
- [X] T009 [P] Write failing integration tests for FastAPI initialization, CORS middleware, and route mounting in tests/integration/test_main.py

### Implementation of Foundational Prerequisites

- [X] T010 Implement application configuration and environment settings via Pydantic Settings in src/config.py (satisfying T005)
- [X] T011 [P] Implement domain enumerations (`DefectCategory`, `SeverityLevel`, `ReviewStatus`) in src/schemas/enums.py citing data-model.md (`DefectCategory`, `SeverityLevel`, `ReviewStatus`) (satisfying T006)
- [X] T012 [P] Implement standardized error response schema and exception models in src/schemas/errors.py citing data-model.md (`ErrorResponse.error_code`, `ErrorResponse.message`, `ErrorResponse.details`) (satisfying T006)
- [X] T013 Implement abstract `LLMClient` protocol and `GroqClient` adapter as sole owner of retry logic (max 2 retries, exponential backoff ~1s and ~2s, no retry on permanent 401/403/config errors) in src/llm/client.py (satisfying T007)
- [X] T014 Implement versioned prompt templates and structured JSON schema instructions for `openai/gpt-oss-120b` (hosted on Groq) in src/llm/prompt.py (satisfying T008)
- [X] T015 Initialize FastAPI application setup, CORS middleware, and API router registration in src/main.py and src/api/v1/router.py (satisfying T009)
- [X] T016 Execute and verify that all Foundational unit and integration tests pass (Red → Green) in tests/

**Checkpoint**: Core foundation ready — User Story 1 implementation can now begin.

---

## Phase 3: User Story 1 - Automated Code Review & Defect Detection (Priority: P1) 🎯 MVP

**Goal**: Accept submitted Python code, execute semantic code review via Groq `openai/gpt-oss-120b`, detect defects across four categories (`BUG`, `SECURITY`, `PERFORMANCE`, `MAINTAINABILITY`) with five severities (`CRITICAL` to `INFO`), enforce deterministic invariants, and return structured `CodeReviewResult`.

**Independent Test**: Submit a Python snippet with a known SQL injection defect and verify HTTP 200 with a `SECURITY` `HIGH` finding; submit clean code and verify HTTP 200 with 0 findings and `PASS` status.

### Tests for User Story 1 (TDD - Tests Written & Failing First) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T017 [P] [US1] Write failing OpenAPI contract test for `POST /api/v1/review` in tests/contract/test_review_contract.py
- [X] T018 [P] [US1] Write failing unit tests for schema validation and finding invariant rules in tests/unit/test_schemas.py
- [X] T019 [P] [US1] Write failing integration tests for normal defect detection and clean code happy paths in tests/integration/test_review_api.py

### Implementation for User Story 1

- [X] T020 [US1] Implement Pydantic finding and request schemas in src/schemas/request.py and src/schemas/response.py citing validation constraints from data-model.md (`CodeReviewRequest.code`, `CodeReviewRequest.file_path`, `CodeReviewRequest.language`, `CodeReviewRequest.include_markdown`, `ReviewFinding.id`, `ReviewFinding.title`, `ReviewFinding.category`, `ReviewFinding.severity`, `ReviewFinding.start_line`, `ReviewFinding.end_line`, `ReviewFinding.description`, `ReviewFinding.recommendation`, `ReviewFinding.confidence`)
- [X] T021 [US1] Implement finding invariant validator and deduplication logic in src/services/review_service.py citing invariant rules from data-model.md
- [X] T022 [US1] Implement review pipeline orchestration service coordinating prompt rendering, Groq client dispatch, parsing, and invariant verification in src/services/review_service.py
- [X] T023 [US1] Implement `POST /api/v1/review` endpoint handler in src/api/v1/review.py
- [X] T024 [US1] Execute and verify that all User Story 1 unit, contract, and integration tests pass (Red → Green) in tests/

**Checkpoint**: User Story 1 is fully functional and delivers a viable standalone MVP increment.

---

## Phase 4: User Story 2 - Input Validation, Secret Sanitization & Error Handling (Priority: P2)

**Goal**: Enforce pre-validation gates (strictly Python language validation, payload size limit of 1,000 lines and 65,536 UTF-8 bytes, pattern-based secret screening with immediate HTTP 422 rejection), deterministically intercept Python AST syntax errors locally with a `CRITICAL` `BUG` finding without calling LLM, and handle bounded retries mapping exhausted provider exceptions to HTTP 502 without duplicate retry logic.

**Independent Test**: Submit code containing API keys -> verify HTTP 422 `SECRET_DETECTED` with no secrets echoed and zero Groq calls; submit invalid Python syntax -> verify HTTP 200 with `CRITICAL` `BUG` finding and `model_id: "deterministic-ast"`; submit oversized code -> verify HTTP 413 `PAYLOAD_TOO_LARGE`; submit non-Python language -> verify HTTP 422 `UNSUPPORTED_LANGUAGE` rejected before AST parsing.

### Tests for User Story 2 (TDD - Tests Written & Failing First) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T025 [P] [US2] Write failing unit tests for pattern-based secret screening in tests/unit/test_secret_scanner.py, verifying credential detection, verifying no secret is echoed or logged, and asserting zero Groq client invocations when secrets are detected
- [X] T026 [P] [US2] Write failing unit tests for deterministic AST syntax verification in tests/unit/test_syntax_checker.py, verifying local `CRITICAL` `BUG` finding generation without calling Groq
- [X] T027 [P] [US2] Write failing integration tests for input validation rejections in tests/integration/test_error_handling.py, asserting unsupported languages are rejected with HTTP 422 before AST parsing, payload size rejection (>1,000 lines or >65,536 UTF-8 bytes -> HTTP 413), and exhausted provider retries return HTTP 502

### Implementation for User Story 2

- [X] T028 [P] [US2] Implement deterministic secret scanner (`SecretScanner`) in src/services/secret_scanner.py covering high-entropy credential patterns (Groq, OpenAI, GitHub PAT, AWS, Private Keys, generic secrets)
- [X] T029 [P] [US2] Implement deterministic Python AST syntax checker (`SyntaxChecker`) in src/services/syntax_checker.py generating `CRITICAL` `BUG` findings without LLM invocation
- [X] T030 [US2] Integrate language validation, payload size guards, secret screening, and AST syntax interception into src/services/review_service.py ensuring AST is never run on non-Python inputs
- [X] T031 [US2] Implement HTTP 502 error mapping for exhausted provider failures in src/api/v1/review.py without duplicate retry logic and without exposing credentials
- [X] T032 [US2] Execute and verify that all User Story 2 tests pass (Red → Green) in tests/

**Checkpoint**: User Stories 1 AND 2 are both fully functional and tested.

---

## Phase 5: User Story 3 - Multi-Format Review Reports & Summary Metrics (Priority: P3)

**Goal**: Aggregate review summary metrics (`ReviewSummary`), calculate overall release quality gate status (`FAIL` if critical/high > 0, else `PASS`), format human-readable Markdown reports on request (`include_markdown: true`), record execution telemetry (`ReviewTelemetry`), and expose healthcheck endpoint.

**Independent Test**: Request review with `include_markdown: true` and verify formatted Markdown output; verify overall status is `FAIL` when critical/high defects exist, and `PASS` otherwise; verify telemetry captures latency and token metadata; verify `GET /api/v1/health` returns HTTP 200.

### Tests for User Story 3 (TDD - Tests Written & Failing First) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T033 [P] [US3] Write failing unit tests for Markdown report generation and quality gate logic in tests/unit/test_reporter.py
- [X] T034 [P] [US3] Write failing integration tests for telemetry recording, markdown formatting, and healthcheck in tests/integration/test_review_api.py

### Implementation for User Story 3

- [X] T035 [US3] Implement `ReviewSummary` and `ReviewTelemetry` schemas in src/schemas/response.py citing fields from data-model.md (`ReviewSummary.status`, `ReviewSummary.total_findings`, `ReviewSummary.critical_count`, `ReviewSummary.high_count`, `ReviewSummary.medium_count`, `ReviewSummary.low_count`, `ReviewSummary.info_count`, `ReviewTelemetry.model_id`, `ReviewTelemetry.prompt_version`, `ReviewTelemetry.latency_ms`, `ReviewTelemetry.prompt_tokens`, `ReviewTelemetry.completion_tokens`, `ReviewTelemetry.total_tokens`, `ReviewTelemetry.retry_count`)
- [X] T036 [US3] Implement Markdown report generator and release gating evaluator (`Reporter`) in src/services/reporter.py
- [X] T037 [US3] Integrate telemetry recording and report generation into src/services/review_service.py and src/api/v1/review.py
- [X] T038 [US3] Implement `GET /api/v1/health` endpoint in src/api/v1/review.py returning service availability status
- [X] T039 [US3] Execute and verify that all User Story 3 tests pass (Red → Green) in tests/

**Checkpoint**: All three User Stories are fully functional and verified.

---

## Phase 6: Evaluation Benchmark Harness & Empirical Validation

**Purpose**: Systematic empirical evaluation of model performance, prompt engineering, and benchmark scoring against ground-truth datasets per Constitution Principle I & V.

**⚠️ CRITICAL**: Strict TDD is enforced for evaluation infrastructure. Evaluation metric scorers and harness runner tests MUST be written and confirmed failing before implementing the scorers and runner.

### Benchmark Setup & Ground Truth Dataset

- [X] T040 [P] Define and freeze evaluation configuration and acceptance thresholds (schema adherence 100%, invariant compliance 100%, precision >=80%, recall >=80%, F1 >=80%, false-positive rate <=15%) in evals/config.json before benchmark execution
- [X] T041 [P] Author ground-truth evaluation benchmark dataset in evals/dataset.json containing at least 15 meaningful, independently verified cases covering 6 required scenario categories (normal, boundary, ambiguous, missing info, malformed/syntax, adversarial/injection)

### Tests for Evaluation Infrastructure (TDD - Written & Failing First) ⚠️

- [X] T042 [P] Write failing unit tests for independent evaluation metric scorers (schema adherence, invariant compliance, precision, recall, F1, false-positive rate) in tests/unit/test_eval_metrics.py
- [X] T043 [P] Write failing unit tests for evaluation harness runner (threshold enforcement, malformed outputs, and result serialization) in tests/unit/test_eval_runner.py

### Implementation of Evaluation Infrastructure & Benchmark Runs

- [X] T044 Implement independent evaluation metric scorers in evals/metrics.py for Dimension A (Schema Adherence: 100%), Dimension B (Deterministic Invariants: 100%), and Dimension C (Semantic Quality: Precision, Recall, F1, False-Positive Rate) (satisfying T042)
- [X] T045 Implement evaluation harness runner in evals/runner.py and execution shell script in .harness/run-evals.sh executing against evals/dataset.json using frozen thresholds (satisfying T043)
- [X] T046 Execute and verify that all evaluation harness unit tests pass (Red → Green) in tests/
- [X] T047 Execute initial baseline evaluation against evals/dataset.json using baseline prompt v1.0.0, capturing prompt version, configuration, raw outputs, and metrics in evidence/initial-generation/eval-results.json and evidence/initial-generation/harness-log.md without modifying dataset or thresholds
- [X] T048 Optimize prompt templates in src/llm/prompt.py based on baseline findings, re-run evaluation harness against the exact same frozen evals/dataset.json and thresholds, and archive final evidence in evidence/final-generation/eval-results.json and evidence/final-generation/harness-log.md while preserving baseline evidence

---

## Phase 7: Polish & Quality Gates Verification

**Purpose**: Execute automated quality gates, verify privacy/secret exclusions, and conduct end-to-end validation across the complete project.

- [X] T049 [P] Execute code formatting and linting checks via `ruff check .` and `ruff format --check .`
- [X] T050 [P] Execute static application security testing via `bandit -c pyproject.toml -r src/` (verify 0 findings)
- [X] T051 [P] Execute dependency vulnerability scan via `pip-audit -r requirements.txt` (verify 0 vulnerabilities)
- [X] T052 Execute complete deterministic automated test suite via `pytest -v` verifying 100% test pass rate
- [X] T053 Verify that secrets, API credentials, and complete source code are excluded from all logs and evidence files (evidence/initial-generation/ and evidence/final-generation/)
- [X] T054 Execute end-to-end quickstart validation scenarios from quickstart.md against running local service and verify all required artifacts (evidence/final-generation/eval-results.json, evidence/final-generation/harness-log.md, evidence/initial-generation/eval-results.json, evidence/initial-generation/harness-log.md) exist and are complete

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion — BLOCKS all user stories
  - Tests (T005–T009) MUST be written and confirmed failing before implementation (T010–T015) begins
- **User Story 1 (Phase 3)**: Depends on Foundational completion — Delivers core MVP
  - Tests (T017–T019) MUST be written and confirmed failing before implementation (T020–T023) begins
- **User Story 2 (Phase 4)**: Depends on User Story 1 completion
  - Tests (T025–T027) MUST be written and confirmed failing before implementation (T028–T031) begins
- **User Story 3 (Phase 5)**: Depends on User Story 1 & 2 completion
  - Tests (T033–T034) MUST be written and confirmed failing before implementation (T035–T038) begins
- **Evaluation Harness (Phase 6)**: Depends on User Story 1, 2, and 3 implementation completion
  - **Threshold & Dataset Prerequisites**: T040 (freeze evaluation configuration and thresholds) and T041 (author independently verified ground-truth dataset) MUST be completed before any live benchmark execution.
  - **TDD Test-First Rule**: T042 and T043 (metric scorers and runner tests) MUST be written and confirmed failing before T044 and T045 implementation begins.
  - **Test Verification Checkpoint**: T046 can execute only after both T044 and T045 are complete, and MUST confirm 100% of evaluation infrastructure tests pass (Red → Green).
  - **Baseline Evaluation Execution**: T047 (baseline evaluation) can execute only after T040, T041, and T046 are complete. It captures initial prompt version, raw outputs, and metrics.
  - **Final Evaluation Execution**: T048 (final evaluation) can execute only after T047 is complete, evaluated against the exact same dataset (T041) and frozen thresholds (T040). Baseline evidence in evidence/initial-generation/ MUST remain unchanged.
  - **Evidence Privacy Mandate**: Raw evaluation evidence in evidence/ MUST NOT expose API credentials, secrets, or complete submitted source code.
- **Polish & Quality Gates (Phase 7)**: Depends on all implementation and evaluation phases complete

### Parallel Opportunities

- **Phase 1**: T003 can run in parallel with T002
- **Phase 2 Tests**: T005, T006, T007, T008, T009 can run in parallel after fixtures (T004) are ready
- **Phase 2 Implementation**: T011 and T012 can run in parallel
- **Phase 3 Tests (US1)**: T017, T018, T019 can run in parallel
- **Phase 4 Tests (US2)**: T025, T026, T027 can run in parallel; T028 and T029 can run in parallel once tests fail
- **Phase 5 Tests (US3)**: T033 and T034 can run in parallel
- **Phase 6**: T040, T041, T042, T043 can run in parallel
- **Phase 7**: T049, T050, T051 can run in parallel

---

## Implementation Strategy

### MVP First (Phases 1, 2, and 3)
1. Complete Phase 1 (Setup) and Phase 2 (Foundational) under strict TDD: tests written and confirmed failing before implementation.
2. Implement Phase 3 (User Story 1) following strict TDD: tests written and confirmed failing first.
3. Validate User Story 1 independently with mocked Groq client — delivers a fully functional standalone MVP.

### Incremental Delivery (Phases 4, 5, 6, 7)
4. Add User Story 2 (pre-validation, secrets, syntax checker, provider error mapping) with tests failing first → Re-validate all tests.
5. Add User Story 3 (telemetry, summary reports, markdown, healthcheck) with tests failing first → Re-validate all tests.
6. Freeze evaluation config, build benchmark dataset (`evals/dataset.json`), run baseline evaluation, capture baseline evidence, optimize prompts, and capture final evidence.
7. Run complete four-gate deterministic harness (Ruff, Bandit, pip-audit, Pytest) and verify privacy/artifact exclusions.
