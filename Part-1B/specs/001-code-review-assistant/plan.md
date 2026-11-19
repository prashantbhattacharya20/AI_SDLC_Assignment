# Implementation Plan: AI Code Review Assistant

**Branch**: `001-code-review-assistant` | **Date**: 2026-11-20 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from [specs/001-code-review-assistant/spec.md](spec.md)

---

## Summary

Build an automated static code analysis service implemented as a modern FastAPI web service powered by Groq Large Language Models utilizing `openai/gpt-oss-120b` (ratified 2026-11-20, replacing placeholder `llama-3.3-70b-versatile`) as the single standardized model for the MVP and all evaluation benchmarks. The service evaluates single-file Python source code or snippets and detects defects across four standardized categories (`BUG`, `SECURITY`, `PERFORMANCE`, `MAINTAINABILITY`) with five severity tiers (`CRITICAL` to `INFO`).

The architecture pairs non-deterministic LLM analysis with strict deterministic pre- and post-validation gates:
1. **Pre-Validation Pipeline**: Language validation (strictly Python; unsupported languages rejected with HTTP 422), dual payload size verification (maximum 1,000 lines and 65,536 UTF-8 bytes; exceeding either returns HTTP 413), high-entropy secret screening (rejecting credentials with HTTP 422 before transmission), and Python AST syntax verification (locally catching syntax errors and generating `CRITICAL` `BUG` findings without invoking the external LLM). Python AST parsing is never run against non-Python source.
2. **Model Integration**: Decoupled `LLMClient` interface utilizing the official Groq SDK with JSON mode (`response_format={"type": "json_object"}`) and bounded retry handling (maximum 2 retries with exponential backoff of ~1s and ~2s for transient network, rate limits, or recoverable schema failures; permanent auth/config errors fail immediately; exhausted retries return HTTP 502).
3. **Post-Validation & Invariants**: Rigid Pydantic v2 schema enforcement, line boundary verification, finding deduplication, and automated release quality gating (`FAIL` if any `CRITICAL` or `HIGH` findings exist). Finding confidence is treated as a model-reported subjective certainty estimate (0.0 to 1.0) rather than a calibrated probability; all schema and invariant checks remain completely independent of the confidence score.

---

## Technical Context

**Language/Version**: Python 3.13.9 (utilizing existing root `.venv313` environment)

**Primary Dependencies**: FastAPI (>=0.110.0), Pydantic v2 (>=2.6.0), Groq Python SDK (`groq`), Uvicorn (>=0.28.0)

**Storage**: Stateless web service; benchmark evaluation datasets (`evals/dataset.json`) and results persisted to file storage (`evidence/`)

**Testing**: Pytest (>=8.0.0), HTTPX TestClient (`httpx`), pytest-mock, unittest.mock

**Target Platform**: Linux / macOS server (Python 3.13.9 runtime)

**Project Type**: Web service (REST API) with OpenAPI 3.1 schema definitions

**Performance Goals**:
- End-to-end p95 response latency < 15 seconds for submissions under 500 lines.
- End-to-end p95 response latency < 30 seconds for submissions up to the 1,000-line ceiling.
- *Measurement Methodology*: Measured from HTTP request receipt to HTTP response dispatch on a warm service instance over a sample of at least 20 consecutive benchmark runs under standard network conditions. These figures represent empirical operational targets rather than contractual SLA guarantees.
- Sub-millisecond execution for local secret screening and AST syntax pre-checks.

**Constraints**:
- Single LLM model: `openai/gpt-oss-120b` (hosted on Groq) exclusively; fallback models (such as `llama-3.1-8b-instant`) are removed.
- Language scope: Python (`python`) is the sole supported language for the MVP. Non-Python submissions are rejected with HTTP 422 (`UNSUPPORTED_LANGUAGE`).
- Payload limits: Enforce both a maximum of 1,000 lines and 65,536 UTF-8 bytes. Exceeding either limit returns HTTP 413 (`PAYLOAD_TOO_LARGE`).
- Offline, deterministic CI tests: All external Groq API interactions MUST be mocked in Pytest.
- Live evaluation harness decoupled in `.harness/` and `evals/` running against `evals/dataset.json` (>=15 cases across 6 scenarios).
- Strict secret hygiene: Immediate HTTP 422 rejection on detected API keys or tokens (`SECRET_DETECTED`); zero source code or sensitive tokens logged.
- Bounded resilience: Maximum 2 retries with exponential backoff (~1s, ~2s) for transient errors; permanent auth/config errors fail immediately; exhausted retries return HTTP 502 (`PROVIDER_ERROR`) without leaking provider internals.

**Scale/Scope**: Single feature MVP; 2 REST endpoints (`GET /api/v1/health`, `POST /api/v1/review`), 5 service modules, 6 evaluation benchmark scenario types

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Principle I: Test-First & Eval-Driven Development (EDD)**: **PASSED**<br>
  Automated unit, contract, and integration tests authored first with mocked responses. Empirical evaluation suite (`evals/dataset.json`) designed with >=15 verified cases covering 6 distinct scenario types. Three independent evaluation dimensions (Dimension A: Schema, Dimension B: Deterministic Invariants, Dimension C: Semantic Quality) evaluated with pre-set acceptance thresholds. Ground-truth outcomes and metrics are never fabricated.
- **Principle II: Modular Architecture & Provider Abstraction**: **PASSED**<br>
  Single-project modular FastAPI layout (`src/api`, `src/services`, `src/schemas`, `src/llm`). Groq is the sole required provider implementation behind a clean `LLMClient` protocol utilizing `openai/gpt-oss-120b`. No premature multi-provider frameworks, microservices, or external database layers.
- **Principle III: Strict Contract & Structured Schema Enforcement**: **PASSED**<br>
  OpenAPI 3.1 contract documented in [contracts/code-review-api.yaml](contracts/code-review-api.yaml) with valid JSON Schema null types. Strict Pydantic v2 data models with deterministic invariant verification (line ranges within source bounds, non-empty fields, duplicate finding suppression). Clear remediation recommendations required instead of complex diffs.
- **Principle IV: Observability, Telemetry & Secret Hygiene**: **PASSED**<br>
  Every review execution records telemetry (exact model ID `openai/gpt-oss-120b` or `deterministic-ast`, latency, prompt version, tokens, retries). Pattern-based secret scanner rejects identifiable credentials before LLM calls. No full source code or secrets logged.
- **Principle V: Spec-Driven Quality Gates & Empirical Benchmarks**: **PASSED**<br>
  Sequential progression strictly followed: Specify (`spec.md`) → Clarify (5/5 ratified in `spec.md`) → Plan (`plan.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md`). Downstream: Tasks (`tasks.md`) → Analyze → Implement.
- **Engineering Constraints & Standards**: **PASSED**<br>
  Python 3.13.9 (`.venv313`), FastAPI, Pydantic v2, Ruff, Bandit SAST, pip-audit, Pytest with mocked Groq client. CLI optional.

---

## Project Structure

### Documentation (this feature)

```text
specs/001-code-review-assistant/
├── spec.md              # Feature specification with ratified clarifications
├── plan.md              # This file (/speckit-plan output)
├── research.md          # Phase 0 architectural decisions & trade-offs
├── data-model.md        # Phase 1 domain entities, schemas & invariants
├── quickstart.md        # Phase 1 runnable validation guide & curl tests
├── checklists/
│   └── requirements.md  # 16/16 quality checklist validation
├── contracts/           # Phase 1 OpenAPI 3.1 contract
│   └── code-review-api.yaml
└── tasks.md             # Phase 2 task breakdown (/speckit-tasks output)
```

### Source Code & Evaluation Layout (Part-1B)

```text
Part-1B/
├── pyproject.toml           # Tooling configuration (Ruff, Bandit, Pytest)
├── requirements.txt         # Runtime and test dependencies (Python 3.13)
├── src/
│   ├── __init__.py
│   ├── main.py              # FastAPI application initialization & exception handlers
│   ├── config.py            # Environment configuration via Pydantic Settings
│   ├── schemas/             # Pydantic v2 domain schemas & invariant models
│   │   ├── __init__.py
│   │   ├── enums.py         # DefectCategory, SeverityLevel, ReviewStatus
│   │   ├── request.py       # CodeReviewRequest (max 1000 lines, 64KB UTF-8 bytes)
│   │   ├── response.py      # ReviewFinding, ReviewSummary, ReviewTelemetry, CodeReviewResult
│   │   └── errors.py        # ErrorResponse (SECRET_DETECTED, UNSUPPORTED_LANGUAGE, etc.)
│   ├── services/            # Business & orchestration logic
│   │   ├── __init__.py
│   │   ├── secret_scanner.py # Pattern-based credential detection & immediate rejection
│   │   ├── syntax_checker.py # Deterministic Python AST parsing & error synthesis
│   │   ├── review_service.py # Core review pipeline orchestration & invariant verification
│   │   └── reporter.py       # Markdown summary generation & quality gate evaluation
│   ├── llm/                 # Provider client & prompt templates
│   │   ├── __init__.py
│   │   ├── client.py        # Abstract LLMClient protocol & GroqClient implementation
│   │   └── prompt.py        # Versioned prompt templates & structured schema instructions
│   └── api/                 # FastAPI HTTP routers
│       ├── __init__.py
│       └── v1/
│           ├── __init__.py
│           ├── router.py    # Route registration
│           └── review.py    # /review and /health endpoint handlers
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # Shared fixtures (mock Groq client, sample code snippets)
│   ├── unit/                # Deterministic unit tests (offline, 0 network)
│   │   ├── test_schemas.py
│   │   ├── test_secret_scanner.py
│   │   ├── test_syntax_checker.py
│   │   └── test_prompt_rendering.py
│   ├── contract/            # OpenAPI 3.1 contract verification tests
│   │   └── test_review_contract.py
│   └── integration/         # FastAPI TestClient mocked end-to-end tests
│       ├── test_review_api.py
│       └── test_error_handling.py
│
├── evals/                   # Ground-truth evaluation benchmarks
│   ├── dataset.json         # Benchmark dataset (>=15 cases across 6 scenarios)
│   ├── runner.py            # Evaluation benchmark execution harness
│   └── metrics.py           # Dimension A/B/C scoring (precision, recall, F1, schema)
│
├── .harness/                # Evaluation harness shell scripts
│   └── run-evals.sh         # Live evaluation harness runner
│
└── evidence/                # Benchmark execution records
    ├── initial-generation/  # Baseline prompt evaluation results
    └── final-generation/    # Optimized prompt evaluation results
```

**Structure Decision**: Selected a cohesive, single-project modular architecture within `Part-1B/` conforming to FastAPI idioms and Constitution Principle II. Strictly decouples schemas, domain services, model provider clients, and HTTP routers while avoiding premature microservices or excessive indirection.

---

## Complexity Tracking

> **No violations recorded.** Architecture strictly adheres to all five Constitution principles and engineering standards.
