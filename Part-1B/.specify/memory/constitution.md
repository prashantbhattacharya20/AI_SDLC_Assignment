<!--
SYNC IMPACT REPORT
==================
Version Change: 1.1.0 -> 1.1.1
Ratification Date: 2026-11-20
Last Amended Date: 2026-11-20

Modified Principles:
- I. Test-First & Eval-Driven Development (EDD): Clarified ground-truth integrity to permit purpose-built or synthetic code examples in evaluation datasets provided labels and expected findings are independently verified, while strictly prohibiting fabricating benchmark outcomes, falsely reporting metrics, or misrepresenting evaluation results.

Added/Refined Sections:
- Engineering Constraints & Standards: Specified Python 3.13.9 using the existing root .venv313 environment as the required development and validation environment, explicitly prohibiting the use of the older Python 3.9 .venv.

Removed Sections/Constraints:
- None

Follow-up TODOs:
- None
-->

# AI Code Review Assistant Constitution

## Core Principles

### I. Test-First & Eval-Driven Development (EDD)
Test-driven development and systematic evaluation harnesses are strictly non-negotiable for all components across deterministic engine logic and non-deterministic LLM interactions.
- Engineers and AI agents MUST write automated test suites and evaluation benchmarks before developing implementation code or prompts.
- Deterministic logic (parsing, AST traversal, finding filtering, schema validation, output formatting) MUST follow strict red-green-refactor TDD cycles with exact assertion unit and integration tests.
- Non-deterministic LLM analysis MUST be governed by evaluation benchmarks (`evals/dataset.json`) containing at least 15 meaningful evaluation cases.
- The evaluation dataset MUST comprehensively cover:
  1. Normal code review scenarios (standard defects and clean idiomatic code).
  2. Boundary conditions (empty files, single-line snippets, large files, deeply nested blocks).
  3. Ambiguous code or under-specified requirements.
  4. Missing mandatory information (partial snippets, unresolved imports).
  5. Malformed or unsupported inputs (syntax errors, non-code text).
  6. Adversarial inputs and guardrail scenarios (prompt injection attempts, obfuscated payloads).
- The evaluation harness (`.harness/`) MUST independently assess three distinct evaluation dimensions:
  - **Dimension A (Structural & Schema Compliance)**: Strict conformance to the declared Pydantic finding and response schemas.
  - **Dimension B (Deterministic Invariants & Property-Based Checks)**: Exact line number validity against source, positive ranges, non-empty fields, valid enum categories/severities, and duplicate finding handling.
  - **Dimension C (Semantic Quality of Generated Findings)**: Meaningful defect identification, precision, recall, F1 score, and false-positive rate against ground-truth findings.
- LLM-as-judge MAY assist in evaluating semantic quality but MUST NOT replace deterministic schema validation or invariant checks.
- Quantitative acceptance thresholds MUST be established in the feature specification or evaluation plan BEFORE benchmark execution.
- Evaluation runs MUST record pass/fail outcomes, quantitative metrics, model configuration, and relevant execution metadata.
- Purpose-built or synthetic code examples are permitted in evaluation datasets, provided expected findings and labels are independently verified. Fabricating benchmark outcomes, falsely reporting metrics, or misrepresenting evaluation results remains strictly prohibited.
*Rationale*: Combining standard TDD for deterministic code with multi-dimensional Eval-Driven Development (EDD) ensures reliable defect detection, prevents hallucinated reports, and enforces empirical quality benchmarks.

### II. Modular Architecture & Provider Abstraction
The Code Review Assistant engine MUST be engineered as a cohesive, modular system within a focused FastAPI application, maintaining decoupled subsystems and clean interface boundaries.
- The engine architecture MUST separate concerns into dedicated modules:
  1. **Source Ingestion & Parsing**: File discovery, AST analysis, context chunking, and diff/source extraction.
  2. **Prompt Orchestration**: Versioned prompt template rendering, task instructions, and schema guidance.
  3. **Model Provider Client**: A clean, decoupled LLM client interface isolating external model communication.
  4. **Analysis & Finding Normalization**: Parsing, schema verification, deterministic invariant validation, deduplication, and severity classification.
  5. **Presentation & Export**: Markdown reports, structured JSON output, and API response serialization.
- **Provider Scope**: Groq MUST be the primary and only required LLM provider implementation for this assignment.
- The client interface MUST remain cleanly decoupled so the model provider can be replaced later if genuinely necessary, but engineers and agents MUST NOT implement OpenAI, Anthropic, Gemini, or local-model integrations as part of this assignment.
- Premature abstractions, unnecessary packages, microservices, and excessive architectural layers MUST be avoided; components MUST reside cleanly within `src/` modules of the FastAPI application.
*Rationale*: A clean, modular design centered around a single high-performance provider (Groq) satisfies assignment objectives with minimal architectural overhead while preserving future extensibility.

### III. Strict Contract & Structured Schema Enforcement
All inter-component communications, LLM interactions, and external data contracts MUST adhere to strict, validated schemas and deterministic invariants.
- LLM outputs MUST be strictly constrained to structured schemas (e.g., Pydantic models specifying finding title, defect category, severity level, file path, line range, explanation, clear remediation recommendation, and confidence score).
- Suggested fix diffs are NOT required if they introduce unnecessary complexity; a clear, actionable remediation recommendation is sufficient.
- **Deterministic Invariants**: Every generated finding and response MUST satisfy non-negotiable invariant rules:
  1. Every finding MUST specify a valid defect category (`BUG`, `SECURITY`, `PERFORMANCE`, `MAINTAINABILITY`).
  2. Every finding MUST specify a valid severity level (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`, `INFO`).
  3. Line numbers MUST be positive integers and strictly consistent with the submitted source code.
  4. Start and end line ranges MUST be logically valid (`start_line <= end_line` and within bounds of the submitted file).
  5. Required fields MUST not be empty or whitespace-only.
  6. Duplicate findings (same category, line range, and defect description) SHOULD be detected and handled consistently.
  7. The complete payload MUST conform to its declared Pydantic/JSON schema; malformed model responses MUST NEVER bypass validation.
- Retry and fallback mechanisms for malformed outputs MUST be bounded (e.g., maximum retry limit) and fully testable with deterministic mocks.
*Rationale*: Explicit deterministic invariants guarantee that only structurally sound, logically valid, and actionable findings are surfaced to developers and automated pipelines.

### IV. Observability, Telemetry & Secret Hygiene
System execution MUST provide full visibility into operational performance, model usage, and evaluation metrics, while enforcing practical and verifiable privacy practices.
- Every review execution and evaluation run MUST emit structured, contextual telemetry:
  - Model identifier and configuration parameters (temperature, max tokens).
  - Versioned prompt identifier and template hash.
  - Token consumption (prompt tokens, completion tokens, total tokens) whenever provided by the provider API.
  - Inference latency and per-stage execution durations.
  - Parsing and validation outcomes (schema pass/fail, invariant validation status).
  - Bounded retry counts and fallback execution triggers.
- **Secret Hygiene & Privacy Standards**:
  - API keys, credentials, and sensitive access tokens MUST NEVER appear in source control, API responses, or system logs.
  - Secrets and credentials MUST be injected exclusively through environment variables and git-excluded `.env` files.
  - The engine MUST implement practical detection and redaction or rejection of identifiable secrets (e.g., API key formats, bearer tokens, private keys) before external transmission to the LLM API.
  - System logs MUST avoid recording complete source code or sensitive payload contents.
  - Systems and documentation MUST NOT claim guaranteed zero retention, complete PII detection, or universal data scrubbing unless technically demonstrated; actual privacy limitations, sanitization rules, and provider behaviors MUST be accurately documented.
*Rationale*: Structured telemetry provides critical visibility into latency and token costs, while pragmatic secret hygiene prevents accidental credential leakage without making unrealistic security claims.

### V. Spec-Driven Quality Gates & Empirical Benchmarks
All feature implementations, prompt refinements, and architecture updates MUST strictly follow the Spec-Driven Development (SDD) lifecycle.
- Work MUST proceed sequentially through the six defined SDD phases:
  1. **Specify**: Define assistant capabilities, supported languages, defect categories, and user stories in `spec.md`.
  2. **Clarify**: Interactively resolve edge cases, unsupported code constructs, and detection trade-offs.
  3. **Plan**: Establish component architecture, prompt strategy, schema definitions, and evaluation designs in `plan.md`.
  4. **Tasks**: Break down the plan into ordered, dependency-tracked work items in `tasks.md`.
  5. **Analyze**: Perform non-destructive cross-artifact consistency checks across `spec.md`, `plan.md`, and `tasks.md` before implementation.
  6. **Implement**: Execute implementation strictly guided by tasks, verifying against TDD tests and benchmark datasets.
- Quantitative acceptance thresholds MUST be established in the feature specification or evaluation plan prior to running benchmark evaluations.
- Prompt engineering MUST be empirical: prompt adjustments MUST compare baseline (initial-generation) vs. optimized (final-generation) benchmark performance on `evals/dataset.json` and archive genuine results in `evidence/`.
- Untracked code modifications or ad-hoc prompt tweaks without corresponding specification items are prohibited.
*Rationale*: Systematic progression through Spec Kit phases prevents scope creep, maintains alignment with assignment goals, and guarantees empirical proof of model quality improvement.

## Engineering Constraints & Standards

All software artifacts within the Part 1B project MUST adhere to the following technical constraints:
- **Language & Runtime**: Python 3.13.9 using the existing root `.venv313` environment as the required development and validation environment. The older Python 3.9 `.venv` MUST NOT be used.
- **Application Framework**: Modern FastAPI web service with standard RESTful endpoints and OpenAPI documentation. Universal or standalone CLI interfaces are optional and NOT mandatory unless explicitly justified by the feature specification.
- **Data Validation & Schemas**: Pydantic v2 for all data structures, review finding schemas, and configuration models.
- **LLM Integration & Testing**:
  - Groq is the sole required provider implementation (`groq` Python client).
  - Deterministic automated tests (unit, contract, integration) and CI workflows MUST use mocked Groq responses to guarantee fast, zero-cost, and deterministic test runs.
  - Live LLM evaluations against the Groq API MUST be kept separate from ordinary deterministic CI test suites.
- **Static Analysis & Quality Gates**:
  - Code formatting and linting: Ruff (`ruff check .`, `ruff format --check .`).
  - Static Application Security Testing: Bandit SAST (`bandit -c pyproject.toml -r src/`) with zero tolerance for high or medium severity findings.
  - Software Composition Analysis: `pip-audit -r requirements.txt` for vulnerability scanning.
  - Automated Testing: Pytest for deterministic unit, integration, and contract tests.
- **Dependency Minimization**: Dependencies MUST be audited for necessity; avoid unnecessary packages, microservices, or speculative frameworks.

## Development Workflow & Evaluation Gates

The development lifecycle enforces structured validation checkpoints prior to accepting any changes:
1. **Specification Traceability**: Every code change, prompt adjustment, or benchmark addition MUST reference its parent specification in `specs/`.
2. **Deterministic Quality Gate (CI & Local)**:
   - `ruff check .` and `ruff format --check .` MUST pass cleanly.
   - `bandit -c pyproject.toml -r src/` MUST report 0 vulnerabilities.
   - `pip-audit -r requirements.txt` MUST report 0 vulnerable dependencies.
   - `pytest -v` MUST pass 100% of unit, contract, and integration tests using mocked provider responses.
3. **LLM Evaluation Harness Gate (Empirical Benchmarks)**:
   - The evaluation runner (`.harness/run-evals.sh` or Python harness) MUST execute against `evals/dataset.json` (minimum 15 cases across all 6 scenario categories).
   - Metrics across all three evaluation dimensions (Structural/Schema Compliance, Deterministic Invariants, Semantic Quality) MUST meet or exceed pre-established acceptance thresholds.
   - Genuine, un-fabricated evaluation results and comparative evidence MUST be archived in `evidence/`.

## Governance

This constitution establishes the authoritative technical standards and architectural laws for Part 1B: AI Code Review Assistant.
- **Supremacy**: The principles and engineering standards defined herein supersede informal preferences, prompt trial-and-error, or undocumented conventions.
- **Review & Gate Enforcement**: All pull requests, automated agent workflows, and manual reviews MUST verify compliance with these core principles. Any deviation or exception MUST be documented with formal rationale.
- **Amendment Procedure**: Amendments to this constitution require a formal proposal, justification, sync impact analysis, and version increment.
- **Versioning Policy**: Semantic versioning (SemVer) applies to this constitution:
  - **MAJOR (`X.0.0`)**: Fundamental changes or deletions of core principles, architectural restructuring, or major governance changes.
  - **MINOR (`X.Y.0`)**: Introduction of new principles, sections, defect categories, or substantially expanded guidance.
  - **PATCH (`X.Y.Z`)**: Non-semantic clarifications, typo fixes, or formatting refinements.

**Version**: 1.1.1 | **Ratified**: 2026-11-20 | **Last Amended**: 2026-11-20
