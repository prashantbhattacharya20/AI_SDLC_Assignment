# AI-Assisted Software Development Life Cycle (AI-SDLC)

**Course**: BITS Pilani WILP
**Assignment**: Assignment 1 (Spec-Driven Development & Harness Engineering)
**Author**: Prashant Bhattacharya
**Repository**: `AI_SDLC_Assignment`
**GitHub URL**: [https://github.com/prashantbhattacharya20/AI_SDLC_Assignment](https://github.com/prashantbhattacharya20/AI_SDLC_Assignment)
**Evaluation Status**: **Both Part-1A and Part-1B Fully Implemented, Verified, and Accepted**

---

## Table of Contents

1. [Repository Overview & Architecture](#1-repository-overview--architecture)
2. [Complete Directory Structure](#2-complete-directory-structure)
3. [Environment Setup & Secure Credential Configuration](#3-environment-setup--secure-credential-configuration)
4. [Part-1A: Expense Management System (MVP)](#4-part-1a-expense-management-system-mvp)
   - [Overview & Architecture](#41-overview--architecture)
   - [Verified Execution & Testing Commands](#42-verified-execution--testing-commands)
   - [Deterministic Validation Harness](#43-deterministic-validation-harness)
   - [Technical Analysis of Error-Handler Repair & Invariant Enforcement](#44-technical-analysis-of-error-handler-repair--invariant-enforcement)
   - [Human Acceptance Verification](#45-human-acceptance-verification)
5. [Part-1B: AI Code Review Assistant](#5-part-1b-ai-code-review-assistant)
   - [Overview & Multi-Stage Defense Architecture](#51-overview--multi-stage-defense-architecture)
   - [Verified Execution & Testing Commands](#52-verified-execution--testing-commands)
   - [Offline Test Suite vs. Live Evaluation Harness](#53-offline-test-suite-vs-live-evaluation-harness)
   - [Evaluation Benchmark Runner & Generated Reports](#54-evaluation-benchmark-runner--generated-reports)
   - [Evaluation Thresholds & Empirical Scorecard](#55-evaluation-thresholds--empirical-scorecard)
   - [Runtime Prompt Version Nuance & Configuration](#56-runtime-prompt-version-nuance--configuration)
   - [Genuine Failure & Repair History](#57-genuine-failure--repair-history)
   - [Human Acceptance Verification](#58-human-acceptance-verification)
6. [Comprehensive Evidence Index](#6-comprehensive-evidence-index)
7. [Continuous Integration (CI) Workflow](#7-continuous-integration-ci-workflow)
8. [Known Limitations & External Dependencies](#8-known-limitations--external-dependencies)

---

## 1. Repository Overview & Architecture

This repository delivers both parts of Assignment 1, demonstrating end-to-end Spec-Driven Development (SDD), Test-Driven Development (TDD), Eval-Driven Development (EDD), and multi-gate harness verification across two isolated sub-projects:

- **Part-1A: Expense Management System (MVP)**
  - A deterministic FastAPI microservice implementing corporate expense claim workflows with SQLite persistence via SQLAlchemy 2.0 and Pydantic v2.
  - Implements 5 strictly scoped endpoints (Submit, List/Filter, Detail with Audit Trail, Approve, Reject). Submitted claims are immutable (no update or delete endpoints).
  - Validated via a 4-gate deterministic harness (Ruff linting/formatting, Bandit SAST, pip-audit SCA, and Pytest).
  - Evaluator Decision: **ACCEPT**.

- **Part-1B: AI Code Review Assistant**
  - An LLM-powered static code analysis assistant combining Groq-hosted open-weight inference (`openai/gpt-oss-120b`) with deterministic pre- and post-validation guards.
  - Employs a multi-stage defense architecture: input language filtering (Python only), dual payload ceilings (1,000 lines / 65,536 UTF-8 bytes), regex credential screening (HTTP 422 rejection, zero LLM calls), local Python AST syntax error interception (CRITICAL defect finding, zero LLM calls), hardware-enforced JSON schema parsing, physical line range boundary verification, finding deduplication, and automated quality gating.
  - Validated via an offline 81-test suite (unit, contract, integration, regression) and an empirical 18-case ground-truth evaluation benchmark spanning 6 scenario archetypes.
  - Evaluator Decision: **ACCEPT**.

---

## 2. Complete Directory Structure

The repository is structured into isolated project directories with dedicated dependencies, virtual environments, tooling configs, and evidence trails:

```text
AI_SDLC_Assignment/
├── README.md                              # Main repository documentation & evaluator guide (this file)
├── .gitignore                             # Universal Git ignore rules (protects secrets, venvs, caches)
├── .github/
│   └── workflows/
│       └── ci.yml                         # Automated multi-gate CI workflow (validates Part-1A)
├── .agents/                               # Spec Kit automation agent skills
│
├── Part-1A/                               # Part-1A: Expense Management System (Accepted)
│   ├── .harness/
│   │   └── run-harness.sh                 # 4-gate deterministic validation harness runner
│   ├── .specify/                          # Spec Kit governance & Constitution v2.0.0
│   │   ├── memory/constitution.md         # Part-1A Constitution
│   │   ├── templates/                     # Specification & planning templates
│   │   └── workflows/                     # Workflow registries
│   ├── specs/001-expense-management/      # Design & governance artifacts
│   │   ├── spec.md                        # Feature specification
│   │   ├── plan.md                        # Implementation plan & architecture gates
│   │   ├── data-model.md                  # Entity relationships & invariants
│   │   ├── contracts/expenses-api.yaml    # OpenAPI 3.0 API contract
│   │   ├── quickstart.md                  # Manual curl validation scenarios
│   │   └── tasks.md                       # Implementation task breakdown
│   ├── src/                               # Application source code
│   │   ├── main.py                        # FastAPI application entry point
│   │   ├── config.py                      # Pydantic Settings configuration
│   │   ├── database.py                    # SQLAlchemy engine & session factory
│   │   ├── models/                        # ORM models (User, Expense, Approval, Audit)
│   │   ├── schemas/                       # Pydantic v2 schemas (Expense, Approval, Common)
│   │   ├── services/                      # Business logic (ExpenseService, AuditService)
│   │   └── api/                           # Route definitions & error handlers
│   ├── tests/                             # Automated test suite (28 tests passing)
│   │   ├── conftest.py                    # Pytest fixtures & in-memory test database
│   │   ├── contract/                      # Contract compliance tests (5 tests)
│   │   ├── integration/                   # Workflow integration tests (20 tests)
│   │   └── unit/                          # Unit validation tests (3 quickstart tests)
│   ├── evidence/                          # Deterministic validation evidence
│   │   ├── harness-log.md                 # Complete verification transcript & ACCEPT sign-off
│   │   ├── initial-generation/README.md   # Baseline execution manifest (4 failed / 4 passed)
│   │   ├── final-generation/README.md     # Final generation manifest (28 passed)
│   │   └── harness-results/               # Preserved raw tool scanner captures
│   │       ├── README.md                  # Results manifest
│   │       └── python313-rerun-evidence.txt # Terminal capture under Python 3.13.9
│   ├── pyproject.toml                     # Tooling configuration (Ruff, Bandit, Pytest)
│   └── requirements.txt                   # Part-1A Python dependencies
│
└── Part-1B/                               # Part-1B: AI Code Review Assistant (Accepted)
    ├── README.md                          # Dedicated Part-1B guide & execution instructions
    ├── .env.example                       # Safe environment template with variable documentation
    ├── .harness/
    │   ├── README.md                      # Evaluation harness documentation
    │   └── run-evals.sh                   # Benchmark runner shell script
    ├── .specify/                          # Spec Kit governance & Constitution v1.1.1
    │   ├── memory/constitution.md         # Part-1B Constitution (TDD, EDD, Invariants)
    │   └── workflows/                     # Workflow registries
    ├── specs/001-code-review-assistant/   # Design & planning artifacts
    │   ├── spec.md                        # Feature specification with 5/5 ratified clarifications
    │   ├── plan.md                        # Architectural plan & component layer design
    │   ├── research.md                    # Phase 0 architectural decisions & trade-offs
    │   ├── data-model.md                  # Domain schemas, invariants, & telemetry entities
    │   ├── contracts/code-review-api.yaml # OpenAPI 3.1 web service contract
    │   ├── quickstart.md                  # End-to-end curl validation scenarios
    │   ├── checklists/requirements.md     # 16/16 specification quality checklist
    │   └── tasks.md                       # 54 ordered implementation tasks (TDD & EDD)
    ├── src/                               # Application source code
    │   ├── main.py                        # FastAPI entry point, CORS, exception handlers
    │   ├── config.py                      # Pydantic Settings with SecretStr credential masking
    │   ├── schemas/                       # Request, response, enum, and error schemas
    │   ├── services/                      # ReviewService, SecretScanner, SyntaxChecker, Reporter
    │   ├── llm/                           # GroqClient adapter, prompt rendering, retry logic
    │   └── api/v1/                        # REST route handlers (/review, /health)
    ├── prompts/                           # Versioned analysis prompts
    │   ├── README.md                      # Prompt versioning manifest
    │   ├── review_system_prompt_v1.txt    # Baseline system prompt (v1.0.0)
    │   ├── review_system_prompt_v2.txt    # Intermediate prompt (v2.0.0 - FPR regression)
    │   └── review_system_prompt_v2_1.txt  # Final active prompt (v2.1.0 - 100% passing)
    ├── tests/                             # Automated test suite (81 tests passing, 100% offline)
    │   ├── conftest.py                    # Mock LLM client & sample code fixtures
    │   ├── contract/                      # OpenAPI 3.1 contract tests (2 tests)
    │   ├── integration/                   # FastAPI TestClient mocked workflow tests (20 tests)
    │   └── unit/                          # Unit tests (schemas, secrets, AST, metrics, 59 tests)
    ├── evals/                             # Empirical evaluation benchmark
    │   ├── README.md                      # Benchmark harness documentation
    │   ├── config.json                    # Frozen acceptance thresholds & evaluation settings
    │   ├── dataset.json                   # Ground-truth evaluation dataset (18 verified cases)
    │   ├── metrics.py                     # Decoupled evaluators for Schema, Invariants, Quality
    │   └── runner.py                      # Benchmark harness engine & report generator
    ├── evidence/                          # Evaluation logs & benchmark manifests
    │   ├── initial-generation/            # Baseline prompt run (v1.0.0, provider error audit)
    │   │   ├── eval-results.json          # Baseline raw outputs & metrics
    │   │   ├── harness-log.md             # Baseline execution log
    │   │   └── README.md                  # Initial generation manifest
    │   ├── v2.0.0-generation/             # Intermediate run (v2.0.0, FPR regression)
    │   │   ├── eval-results.json          # v2.0.0 raw outputs & metrics
    │   │   ├── harness-log.md             # v2.0.0 execution log
    │   │   └── README.md                  # v2.0.0 generation manifest
    │   ├── final-generation/              # Final live benchmark run (v2.1.0 - PASS)
    │   │   ├── eval-results.json          # Final raw model responses & 100% metrics
    │   │   ├── harness-log.md             # Final execution transcript & ACCEPT sign-off
    │   │   └── README.md                  # Final generation manifest
    │   └── revalidated-independent/       # Independent verification run (v2.1.0 - PASS)
    │       ├── eval-results.json          # Re-validation raw outputs & metrics
    │       └── harness-log.md             # Re-validation execution transcript
    ├── pyproject.toml                     # Tooling configuration (Ruff, Bandit, Pytest)
    └── requirements.txt                   # Part-1B Python 3.13 dependencies
```

---

## 3. Environment Setup & Secure Credential Configuration

### 3.1 Python Runtime Requirements

The two sub-projects have specific Python runtime requirements:

| Sub-Project | Minimum Python Version | Primary Target Runtime | Rationale |
| :--- | :--- | :--- | :--- |
| **Part-1A** | Python >= 3.9 | Python 3.9.6 / 3.13.9 | Configured with `requires-python = ">=3.9"`; verified across Python 3.9, 3.10, 3.11, and 3.13.9. |
| **Part-1B** | Python >= 3.13 | Python 3.13.9 | Configured with `requires-python = ">=3.13"`; requires `enum.StrEnum`, `datetime.UTC`, and PEP 604 union types. |

The repository contains two pre-configured virtual environments:
- `.venv`: Python 3.9.6 (used for baseline Part-1A validation)
- `.venv313`: Python 3.13.9 (used for Part-1A re-validation and Part-1B development/evaluation)

You may also create fresh virtual environments as shown below.

---

### 3.2 Part-1A Dependency Installation

```bash
# Option A: Activate existing Python 3.13 or 3.9 environment
source .venv313/bin/activate
# or: source .venv/bin/activate

# Option B: Create a fresh virtual environment
python3 -m venv .venv-part1a
source .venv-part1a/bin/activate

# Install Part-1A dependencies
cd Part-1A
pip install --upgrade pip
pip install -r requirements.txt
cd ..
```

---

### 3.3 Part-1B Dependency Installation

```bash
# Option A: Activate existing Python 3.13 environment
source .venv313/bin/activate

# Option B: Create a fresh Python 3.13 virtual environment
python3.13 -m venv .venv-part1b
source .venv-part1b/bin/activate

# Install Part-1B dependencies
cd Part-1B
pip install --upgrade pip
pip install -r requirements.txt
cd ..
```

---

### 3.4 Secure Groq API Key Configuration (Part-1B)

> [!CAUTION]
> **CRITICAL SECURITY REQUIREMENT: NEVER COMMIT SECRETS TO GIT**
> Under no circumstances should your actual Groq API key (`GROQ_API_KEY`) or any `.env` file be committed to GitHub or shared in plain text. The root `.gitignore` explicitly excludes `.env` and `*.env` files. Verify that `git status` remains clean after configuring your local environment.

Part-1B interacts with Groq Cloud infrastructure to run LLM inferences using model `openai/gpt-oss-120b`.

#### Step 1: Copy the Template
```bash
cp Part-1B/.env.example Part-1B/.env
```

#### Step 2: Configure Your Credentials
Edit `Part-1B/.env` and replace the placeholder with your valid Groq API key:

```env
# Groq Cloud API Credentials (Required for live LLM evaluation and live review service)
GROQ_API_KEY=gsk_your_actual_groq_api_key_here

# Runtime Settings
MODEL_ID=openai/gpt-oss-120b
APP_ENV=development
APP_HOST=127.0.0.1
APP_PORT=8000
PROMPT_VERSION=v2.1.0
MAX_PAYLOAD_LINES=1000
MAX_PAYLOAD_BYTES=65536
GROQ_MAX_RETRIES=2
GROQ_BACKOFF_FACTOR=1.0
```

#### Step 3: Alternatively, Export via Shell Session
If you prefer not to create a local `.env` file, export the key in your terminal session:

```bash
export GROQ_API_KEY="gsk_your_actual_groq_api_key_here"
```

#### Credential Protection in Application Code
- Loaded via Pydantic `SecretStr` in [Part-1B/src/config.py](Part-1B/src/config.py). Calling `repr()`, `str()`, or serializing `Settings` automatically outputs `**********` rather than the raw secret.
- Application logging and telemetry explicitly exclude API tokens.
- The `SecretScanner` pre-validation gate actively screens incoming code payloads for leaked credentials (including Groq, AWS, GitHub, and private keys) and immediately aborts with HTTP 422 before any external API call is initiated.

---

## 4. Part-1A: Expense Management System (MVP)

### 4.1 Overview & Architecture

Part-1A provides a deterministic, auditable corporate expense management service:
- **Framework & ORM**: FastAPI, SQLAlchemy 2.0, SQLite persistence, Pydantic v2.
- **Financial Standard**: Strict **INR (₹)** currency enforcement with paise precision (`Decimal(12, 2)`).
- **Core Endpoints**:
  1. `POST /api/v1/expenses`: Submit a new expense claim.
  2. `GET /api/v1/expenses`: Filter and list expenses (role-based visibility).
  3. `GET /api/v1/expenses/{id}`: Detailed expense view including complete audit history.
  4. `POST /api/v1/expenses/{id}/approve`: Manager approval workflow (prohibits self-approval).
  5. `POST /api/v1/expenses/{id}/reject`: Manager rejection workflow (requires non-empty justification).
- **Immutability Invariant**: Per specification, submitted claims are strictly immutable. No `PUT`, `PATCH`, or `DELETE` endpoints exist; attempts to alter or delete return HTTP 405.

---

### 4.2 Verified Execution & Testing Commands

All commands below are verified to run directly from the `Part-1A/` directory.

#### Start the Part-1A FastAPI Application
```bash
cd Part-1A
uvicorn src.main:app --host 127.0.0.1 --port 8000 --reload
```
- Interactive Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- Alternative ReDoc: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
- OpenAPI Specification: [http://127.0.0.1:8000/openapi.json](http://127.0.0.1:8000/openapi.json)

#### Run the Pytest Verification Suite
```bash
cd Part-1A
pytest -v
```
- **Expected Outcome**: **28 passed**, 0 failed in ~0.21 seconds (9 non-fatal Starlette deprecation warnings regarding HTTP 422 naming conventions and testclient packaging).

#### Run Individual Code Quality & Security Scanners
```bash
cd Part-1A

# 1. Ruff Linting Check
ruff check .

# 2. Ruff Formatting Check
ruff format --check .

# 3. Bandit Static Application Security Testing (SAST)
bandit -c pyproject.toml -r src/

# 4. pip-audit Software Composition Analysis (SCA)
pip-audit -r requirements.txt
```

---

### 4.3 Deterministic Validation Harness

The deterministic harness runner executes all four quality gates sequentially:

```bash
cd Part-1A
./.harness/run-harness.sh
```

*(Alternatively, run from repository root: `Part-1A/.harness/run-harness.sh`)*

#### Summary of Harness Gate Results

| Gate | Tool | Target | Result in Python 3.13.9 | Result in Python 3.9.6 | Disposition |
| :--- | :--- | :--- | :---: | :---: | :---: |
| **Gate 1** | Ruff | `.` | All checks passed; 51 files clean | 17 errors in initial run (fixed) | PASS |
| **Gate 2** | Bandit | `src/` | 656 lines scanned; 0 issues | 666 lines scanned; 0 issues | PASS |
| **Gate 3** | pip-audit | `requirements.txt` | No known vulnerabilities found | 21 baseline advisories (remediated) | PASS |
| **Gate 4** | Pytest | `tests/` | 28 passed, 0 failed (0.21s) | 4 passed, 4 failed in initial run (fixed) | PASS |
| **Final** | Human Decision | Full System | **ACCEPT** | Recorded in [harness-log.md](Part-1A/evidence/harness-log.md) | **ACCEPTED** |

> [!NOTE]
> **Technical Breakdown of Ruff Formatted File Counts (33 `.py` Files; 47 vs. 51 Total Files)**:
> - **Python Source Files**: Part-1A contains strictly **33 Python (`.py`) files** (21 modules in `src/` and 12 test modules in `tests/`). This count has remained strictly invariant throughout Git history.
> - **Embedded Code Block Formatting (Not Prose)**: In `Part-1A/pyproject.toml`, Ruff is configured under `[tool.ruff]` and `[tool.ruff.format]` without custom `include` overrides. As a result, Ruff 0.17.5 uses its default file resolver pattern (`file_resolver.include = ["*.py", "*.pyi", "*.ipynb", "**/pyproject.toml", "**/ruff.toml", "**/.ruff.toml", "*.md"]`). When encountering Markdown (`.md`) files, Ruff checks Python files and supported Python code blocks in Markdown files, where configured; it does **not** format ordinary Markdown prose.
> - **The 47 vs. 51 File Count Lineage**:
>   1. **47 Files (Historical Re-Validation Snapshot)**: When the re-validation rerun was captured in [`Part-1A/evidence/harness-results/python313-rerun-evidence.txt`](Part-1A/evidence/harness-results/python313-rerun-evidence.txt), Ruff evaluated the **33 `.py` files** plus **14 specification and governance `.md` files** in `.specify/` and `specs/` (33 + 14 = 47 files).
>   2. **51 Files (Current Complete Repository)**: After the rerun, four post-validation evidence manifest and log files were authored in `Part-1A/evidence/` (`final-generation/README.md`, `initial-generation/README.md`, `harness-results/README.md`, and `harness-log.md`). Ruff now evaluates all **33 `.py` files** plus **18 `.md` files** (33 + 18 = 51 files). Both figures reflect 100% clean formatting states for all Python code at their respective repository milestones.

---

### 4.4 Technical Analysis of Error-Handler Repair & Invariant Enforcement

#### Investigation of Previous Discrepancies
Previous documentation contained seemingly conflicting summaries of the error handler repair applied during Phase 4 (T039): one summary described the repair as converting exception details using `str(exc)`, while another cited the use of `jsonable_encoder`.

Inspection of the actual source code in [`Part-1A/src/api/errors.py`](Part-1A/src/api/errors.py#L32-L51), the Git history (`3bfa1d1`), and [`Part-1A/evidence/harness-log.md`](Part-1A/evidence/harness-log.md#4-repairs-applied--re-validation-gate-executions-t039) reveals that **both mechanisms are implemented and operate together**:

```python
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_request: Request, exc: RequestValidationError):
    errors = exc.errors()
    messages = []
    clean_errors = []
    for err in errors:
        loc = " -> ".join(str(item) for item in err.get("loc", []))
        msg = str(err.get("msg", "Validation error"))
        messages.append(f"{loc}: {msg}")

        # 1. Explicit Exception Context Stringification
        clean_err = {k: v for k, v in err.items() if k != "ctx"}
        if "ctx" in err:
            clean_err["ctx"] = {k: str(v) for k, v in err["ctx"].items()}
        clean_errors.append(clean_err)

    # 2. FastAPI jsonable_encoder Encoding
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({"detail": "; ".join(messages), "errors": clean_errors}),
    )
```

1. **Root Cause of Baseline Failure**: Under Pydantic v2, custom `@field_validator` methods (such as those checking for positive amounts, paise precision, and past dates in `ExpenseCreate`) embed the raw Python `ValueError` instance inside the error dictionary's `ctx` map. When Starlette's `JSONResponse` attempts to serialize this dictionary via `json.dumps()`, it crashes with `TypeError: Object of type ValueError is not JSON serializable`, causing HTTP 500 errors instead of clean HTTP 422 validation responses.
2. **Dual-Layer Technical Fix**:
   - **Layer 1 (Context Sanitization)**: Iterates over `err["ctx"]` and explicitly converts each value into a string (`clean_err["ctx"] = {k: str(v) for k, v in err["ctx"].items()}`). This converts the raw `ValueError` object into its string representation.
   - **Layer 2 (JSON Encoding)**: Encloses the sanitized dictionary inside `jsonable_encoder(...)` before handing it off to `JSONResponse`, ensuring complete serialization safety across Starlette and FastAPI versions.

---

### 4.5 Human Acceptance Verification

As documented in [`Part-1A/evidence/harness-log.md#55-human-security-verification-and-acceptance`](Part-1A/evidence/harness-log.md#55-human-security-verification-and-acceptance):
- **Decision**: **ACCEPT**
- **Date**: 19th November 2026
- **Reviewer**: Prashant Bhattacharya
- **Scope of Acceptance**: Formally accepted as satisfying all functional requirements, input validations, immutability constraints, and the four deterministic quality gates for the educational MVP assignment. The acceptance explicitly notes that automated static scanners (Bandit, pip-audit) cannot guarantee absolute security against undiscovered zero-day vulnerabilities or business-logic flaws, and this disposition does not constitute production commercial certification.

---

## 5. Part-1B: AI Code Review Assistant

### 5.1 Overview & Multi-Stage Defense Architecture

Part-1B implements an intelligent static analysis engine that pairs non-deterministic LLM reasoning with deterministic pre- and post-validation guardrails:

```
[ Incoming Source Code Submission ]
              │
              ▼
    [ Pre-Validation Guard 1 ] ── Language is Python? ──► (No: HTTP 422 UnsupportedLanguageError)
              │ (Yes)
              ▼
    [ Pre-Validation Guard 2 ] ── Lines <= 1000 & Bytes <= 65536? ──► (No: HTTP 413 PayloadTooLargeError)
              │ (Yes)
              ▼
    [ Pre-Validation Guard 3 ] ── SecretScanner Regex Check ──► (Detected: HTTP 422 SecretDetectedError, ZERO LLM calls)
              │ (Clean)
              ▼
    [ Pre-Validation Guard 4 ] ── Python AST Syntax Check ──► (Fatal Syntax Error: Returns CRITICAL Bug finding, ZERO LLM calls)
              │ (Valid Syntax)
              ▼
    [ LLM Semantic Analysis ]  ── Groq API (openai/gpt-oss-120b, JSON mode, max 2 retries)
              │
              ▼
    [ Post-Validation Guard 5 ] ── Invariant Enforcement:
                                    • Pydantic v2 Schema Conformity
                                    • Physical Line Bounds (1 <= start_line <= end_line <= total_lines)
                                    • Duplicate Finding Suppression
                                    • Summary Status Computation (FAIL if any CRITICAL/HIGH findings)
              │
              ▼
[ Structured JSON Response + Markdown Report ]
```

---

### 5.2 Verified Execution & Testing Commands

All commands below are verified to run directly from the `Part-1B/` directory.

#### Start the Part-1B FastAPI Application
Ensure `GROQ_API_KEY` is configured (see [Section 3.4](#34-secure-groq-api-key-configuration-part-1b)), then start the server:

```bash
cd Part-1B
uvicorn src.main:app --host 127.0.0.1 --port 8000 --reload
```
- Interactive Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- Alternative ReDoc: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
- OpenAPI Specification: [http://127.0.0.1:8000/openapi.json](http://127.0.0.1:8000/openapi.json)

#### Submit a Code Review Request via curl
```bash
curl -X POST http://127.0.0.1:8000/api/v1/review \
  -H "Content-Type: application/json" \
  -d '{
    "code": "def divide(a, b):\n    return a / b\n",
    "language": "python",
    "file_path": "math_utils.py",
    "include_markdown": true
  }'
```

---

### 5.3 Offline Test Suite vs. Live Evaluation Harness

It is essential to distinguish between the **Pytest test suite** and the **Evaluation Benchmark harness**:

| Dimension | Pytest Automated Test Suite | Evaluation Benchmark Harness |
| :--- | :--- | :--- |
| **Purpose** | Unit, contract, integration, and regression verification | Empirical LLM benchmark scoring against ground-truth dataset |
| **Runner Command** | `pytest -v` | `./.harness/run-evals.sh final` or `python -m evals.runner` |
| **API Key Needed?** | **NO (100% Offline)** — all tests use mocks (`MockLLMClient`, `AsyncMock`) | **YES** — requires live `GROQ_API_KEY` to query `openai/gpt-oss-120b` |
| **Test Cases / Scope** | **81 tests** across unit, contract, integration, regression modules | **18 cases** in `evals/dataset.json` scored across 3 dimensions |
| **Execution Time** | ~0.30 seconds | ~45 – 60 seconds (subject to external inference latency) |

#### Running the Offline Test Suite (81 Tests)
The complete Pytest suite executes without network calls or external API keys:

```bash
cd Part-1B

# Run all 81 tests
pytest -v

# Or run individual test categories:
pytest tests/unit/ -v                                # 59 unit tests (schemas, secrets, AST, metrics)
pytest tests/contract/ -v                            # 2 OpenAPI 3.1 contract tests
pytest tests/integration/ -v                         # 20 mocked FastAPI TestClient integration tests
pytest tests/unit/test_adversarial_regression.py -v # 5 adversarial regression tests
```

- **Confirmed Test Count**: **81 passed**, 0 failed in ~0.30 seconds.
  *(Note: An earlier development draft reported 66 tests before the evaluation runner, metric scorers, and adversarial regression test fixtures were completed. The verified reproducible test count is 81.)*

#### Running Static Linters & Security Scans
```bash
cd Part-1B

# 1. Ruff Linting Check
ruff check src evals tests

# 2. Ruff Formatting Check
ruff format --check src evals tests

# 3. Bandit SAST Security Scan
bandit -c pyproject.toml -r src

# 4. pip-audit Dependency Vulnerability Scan
pip-audit -r requirements.txt
```
- **Observed Results**: Ruff: 0 errors across `src`, `evals`, `tests` (48 files clean); Bandit: 928 lines scanned, 0 issues; pip-audit: No known vulnerabilities found.

---

### 5.4 Evaluation Benchmark Runner & Generated Reports

The evaluation harness evaluates live model responses against the frozen 18-case ground-truth dataset in [Part-1B/evals/dataset.json](Part-1B/evals/dataset.json) using acceptance criteria in [Part-1B/evals/config.json](Part-1B/evals/config.json).

#### Running via Shell Script
```bash
cd Part-1B
export GROQ_API_KEY="gsk_your_actual_key"

# Run final evaluation using active prompt v2.1.0:
./.harness/run-evals.sh final

# (Or run baseline evaluation using v1.0.0):
./.harness/run-evals.sh baseline
```

#### Running Directly via Python Module
```bash
cd Part-1B
export GROQ_API_KEY="gsk_your_actual_key"

# Final benchmark run:
python -m evals.runner --mode final

# Explicit parameter invocation:
python -m evals.runner \
  --mode final \
  --dataset evals/dataset.json \
  --config evals/config.json \
  --prompt-version v2.1.0 \
  --output-dir evidence/final-generation
```

#### Dataset Clarifications
- **Evaluation Dataset**: Consists strictly of the **original 18-case ground-truth dataset** (`Part-1B/evals/dataset.json`) covering 6 scenario archetypes (Normal, Boundary, Ambiguous, Missing Context, Malformed Syntax, Adversarial).
- **Adversarial Regression Fixtures**: The **five adversarial regression fixtures** are implemented as automated Pytest tests in [Part-1B/tests/unit/test_adversarial_regression.py](Part-1B/tests/unit/test_adversarial_regression.py) and are completely separate from the frozen 18-case evaluation dataset.

#### Decoupled Validation & Provider Error Handling Logic
In [`Part-1B/evals/metrics.py`](Part-1B/evals/metrics.py) and [`Part-1B/evals/runner.py`](Part-1B/evals/runner.py):
1. **Schema & Invariant Decoupling**: Functions `validate_schema()` and `validate_invariants()` are pure Python validators executing independently of any LLM judge or evaluator prompt.
2. **Strict Provider Error Accounting**: Provider failures (such as HTTP 502, timeouts, or connection drops) are flagged with `is_unevaluable = True`. They are explicitly excluded from the semantic predictions confusion matrix (TP, FP, FN, TN). A non-zero provider error count forces `threshold_eval["zero_provider_errors"] = False`, guaranteeing an overall **FAIL** disposition.
3. **Zero-Evaluable Prevention**: If zero cases evaluate cleanly (`len(predictions) == 0`), the metric scorers return `0.0` and the harness fails, preventing a false PASS.

---

### 5.5 Evaluation Thresholds & Empirical Scorecard

The final evaluation was conducted live against Groq (`openai/gpt-oss-120b`) using ratified prompt `review_system_prompt_v2_1.txt` (`v2.1.0`):

| Evaluation Dimension | Metric | Predeclared Threshold | Observed Score | Gate Status |
| :--- | :--- | :---: | :---: | :---: |
| **Dimension A** | Schema Adherence | 100.0% | **100.0%** (18/18) | ✓ **PASS** |
| **Dimension B** | Invariant Compliance | 100.0% | **100.0%** (18/18) | ✓ **PASS** |
| **Dimension C** | Precision | >= 80.0% | **100.0%** (14/14) | ✓ **PASS** |
| **Dimension C** | Recall | >= 80.0% | **100.0%** (14/14) | ✓ **PASS** |
| **Dimension C** | F1 Score | >= 80.0% | **100.0%** | ✓ **PASS** |
| **Dimension C** | False-Positive Rate | <= 15.0% | **0.0%** (0/4) | ✓ **PASS** |
| **Performance** | p95 Latency | <= 15,000 ms | **8,852.05 ms** | ✓ **PASS** |
| **Performance** | Average Latency | Informational | **2,677.56 ms** | — |
| **Reliability** | Provider Errors | 0 errors | **0 errors** | ✓ **PASS** |
| **Overall Gate** | Release Quality Gate | All Gates Pass | **ALL PASS** | 🟢 **PASS** |

#### Confusion Matrix Summary
- **Total Cases Evaluated**: 18 / 18
- **True Positives (TP)**: 14 (all defect-containing cases accurately detected)
- **True Negatives (TN)**: 4 (all clean cases accurately classified as clean)
- **False Positives (FP)**: 0 (zero clean cases falsely flagged)
- **False Negatives (FN)**: 0 (zero defect cases missed)
- **Unevaluable / Provider Errors**: 0

---

### 5.6 Runtime Prompt Version Nuance & Configuration

During audit inspection of the FastAPI runtime metadata and evaluation harness configuration, a subtle configuration nuance was identified:

- **The Configuration Nuance**:
  - In [`Part-1B/src/config.py`](Part-1B/src/config.py#L63), the default application setting for `PROMPT_VERSION` is `"v1.0.0"`, and [`.env.example`](Part-1B/.env.example#L8) specifies `PROMPT_VERSION=v1.0.0`.
  - When the FastAPI web service is launched without an explicit environment override, `get_review_service()` instantiates `ReviewService()`, which reads `self.settings.PROMPT_VERSION` (`"v1.0.0"`). Consequently, the response telemetry reports `"prompt_version": "v1.0.0"`.
  - Conversely, the evaluation benchmark runner in [`Part-1B/evals/runner.py`](Part-1B/evals/runner.py#L365) explicitly sets `prompt_version = "v2.1.0"` during `--mode final` execution, querying Groq with the ratified `review_system_prompt_v2_1.txt` template.
- **Guidance for Evaluators**:
  - To run the live FastAPI web service with the final repaired prompt `v2.1.0`, ensure `PROMPT_VERSION=v2.1.0` is specified in `Part-1B/.env` (as shown in [Section 3.4](#34-secure-groq-api-key-configuration-part-1b)) or export `export PROMPT_VERSION="v2.1.0"` in your shell before starting `uvicorn`.
  - If omitted, the web service functions correctly but uses the baseline prompt template and reports `v1.0.0`.

---

### 5.7 Genuine Failure & Repair History

In strict accordance with Constitution Principle I (*"Never manufacture failures or benchmark results"*), the repository preserves an auditable record of genuine failure discovery, root-cause investigation, and engineering repair:

1. **Initial Baseline Run (`v1.0.0`)**:
   - Evaluated prompt `review_system_prompt_v1.txt` against `llama-3.3-70b-versatile`.
   - **Observed Outcome**: 14 of 18 cases failed due to upstream Groq account model unavailability (HTTP 502 / account 404). An accounting defect in the initial runner was detected and documented in [Part-1B/evidence/initial-generation/harness-log.md](Part-1B/evidence/initial-generation/harness-log.md).
   - Gate status: 🔴 **FAIL**.

2. **Intermediate Evaluation (`v2.0.0`)**:
   - Model migrated to `openai/gpt-oss-120b` with optimized prompt `review_system_prompt_v2.txt`.
   - **Observed Outcome**: High precision (93.3%), 100% recall, 100% schema adherence, and 100% invariant compliance. However, the False-Positive Rate reached **25.0%** (1 FP out of 4 clean cases), violating the <= 15.0% threshold.
   - **Root Cause Analysis (`TC-ADV-03`)**: Clean code containing a prompt-extraction docstring (`leak_prompt`) was erroneously flagged as `[SECURITY] [HIGH] Hardcoded sensitive data exposed` because prompt v2.0.0 treated prompt injections in comments as code defects rather than passive untrusted input, and lacked explicit rules distinguishing harmless placeholders (`'sensitive_data'`) from real credentials.
   - Preserved in [Part-1B/evidence/v2.0.0-generation/harness-log.md](Part-1B/evidence/v2.0.0-generation/harness-log.md).
   - Gate status: 🔴 **FAIL**.

3. **Engineering Repair (`v2.1.0`)**:
   - Upgraded to `v2.1.0` in [Part-1B/prompts/review_system_prompt_v2_1.txt](Part-1B/prompts/review_system_prompt_v2_1.txt) with:
     - **Passive Untrusted Code Rule**: Mandates that comments and docstrings be treated as passive untrusted data that must not alter reviewer behavior or be reported as code defects.
     - **Secret Identification Rule**: Clarifies that only genuine, high-entropy credentials should be flagged, explicitly exempting mock placeholders like `'sensitive_data'`.
     - **Regression Suite**: Added 5 automated unit tests in [Part-1B/tests/unit/test_adversarial_regression.py](Part-1B/tests/unit/test_adversarial_regression.py).
   - Re-evaluation achieved **0.0% FPR**, **100% Precision**, **100% Recall**, and 🟢 **PASS** across all dimensions, confirmed in [Part-1B/evidence/final-generation/harness-log.md](Part-1B/evidence/final-generation/harness-log.md).

---

### 5.8 Human Acceptance Verification

As documented in [`Part-1B/evidence/final-generation/harness-log.md#7-final-human-review-and-decision`](Part-1B/evidence/final-generation/harness-log.md#7-final-human-review-and-decision):
- **Decision**: **ACCEPT**
- **Date**: 20th November 2026
- **Reviewer**: Prashant Bhattacharya
- **Scope of Acceptance**: Accepted following complete review of final empirical benchmark results (100% schema adherence, 100% invariant compliance, 100% precision/recall/F1, 0% FPR, 81 passing unit/contract/integration tests), independent schema and invariant validation, and regression suites. Acceptance explicitly notes documented limitations regarding external cloud dependencies, non-zero inference latencies (~8.85s p95), and the continuous necessity of human-in-the-loop review.

---

## 6. Comprehensive Evidence Index

The table below provides a navigation index linking directly to all verified evidence files across both sub-projects:

| Project | Evidence Lifecycle Stage | Artifact File Link | Key Result / Summary |
| :--- | :--- | :--- | :--- |
| **Part-1A** | Initial Generation | [Part-1A/evidence/initial-generation/README.md](Part-1A/evidence/initial-generation/README.md) | Baseline manifest; links to initial scanner logs. |
| **Part-1A** | Baseline Failure Evidence | [Part-1A/evidence/harness-log.md#2-baseline-harness-execution-initial-run](Part-1A/evidence/harness-log.md#2-baseline-harness-execution-initial-run) | 4 of 8 tests failed (`ValueError` serialization); 17 Ruff lint errors; 21 pip-audit advisories. |
| **Part-1A** | Observations & Root Cause | [Part-1A/evidence/harness-log.md#3-baseline-failure-evidence--student-observations-t038](Part-1A/evidence/harness-log.md#3-baseline-failure-evidence--student-observations-t038) | Student root-cause analysis for Pytest, Ruff, Bandit, and pip-audit. |
| **Part-1A** | Repairs & Gate Rerun | [Part-1A/evidence/harness-log.md#4-repairs-applied--re-validation-gate-executions-t039](Part-1A/evidence/harness-log.md#4-repairs-applied--re-validation-gate-executions-t039) | Dual fix: `ctx` stringification + `jsonable_encoder`; Ruff cleaned; pyproject.toml adjusted. |
| **Part-1A** | Final Generation Manifest | [Part-1A/evidence/final-generation/README.md](Part-1A/evidence/final-generation/README.md) | Final verified generation state manifest. |
| **Part-1A** | Final Raw Scanner Capture | [Part-1A/evidence/harness-results/python313-rerun-evidence.txt](Part-1A/evidence/harness-results/python313-rerun-evidence.txt) | Complete unedited terminal capture under Python 3.13.9. |
| **Part-1A** | Harness Results Manifest | [Part-1A/evidence/harness-results/README.md](Part-1A/evidence/harness-results/README.md) | Manifest describing preserved raw outputs. |
| **Part-1A** | Final Validation Disposition | [Part-1A/evidence/harness-log.md#5-final-validation-evidence--security-disposition-t040](Part-1A/evidence/harness-log.md#5-final-validation-evidence--security-disposition-t040) | 28 passed, 0 failed; Ruff clean; Bandit 0 findings; pip-audit clean. |
| **Part-1A** | Final Human Decision | [Part-1A/evidence/harness-log.md#55-human-security-verification-and-acceptance](Part-1A/evidence/harness-log.md#55-human-security-verification-and-acceptance) | Decision: **ACCEPT** (Signed: Prashant Bhattacharya, 19-Nov-2026). |
| **Part-1B** | Initial Generation Manifest | [Part-1B/evidence/initial-generation/README.md](Part-1B/evidence/initial-generation/README.md) | Initial baseline run manifest with audit notice. |
| **Part-1B** | Initial Harness Log | [Part-1B/evidence/initial-generation/harness-log.md](Part-1B/evidence/initial-generation/harness-log.md) | Baseline log: FAIL (14 provider errors on `llama-3.3-70b-versatile`). |
| **Part-1B** | Initial Raw Results | [Part-1B/evidence/initial-generation/eval-results.json](Part-1B/evidence/initial-generation/eval-results.json) | Baseline JSON results. |
| **Part-1B** | v2.0.0 Generation Manifest | [Part-1B/evidence/v2.0.0-generation/README.md](Part-1B/evidence/v2.0.0-generation/README.md) | Manifest for intermediate run documenting FPR regression. |
| **Part-1B** | v2.0.0 Harness Log | [Part-1B/evidence/v2.0.0-generation/harness-log.md](Part-1B/evidence/v2.0.0-generation/harness-log.md) | Intermediate log: FAIL (FPR 25.0% > 15.0% threshold due to `TC-ADV-03`). |
| **Part-1B** | v2.0.0 Raw Results | [Part-1B/evidence/v2.0.0-generation/eval-results.json](Part-1B/evidence/v2.0.0-generation/eval-results.json) | Intermediate raw JSON metrics. |
| **Part-1B** | Repair History Documentation | [Part-1B/evidence/final-generation/harness-log.md#3-genuine-failure-and-repair-history](Part-1B/evidence/final-generation/harness-log.md#3-genuine-failure-and-repair-history) | Detailed root cause analysis, prompt v2.1.0 repair, and regression coverage. |
| **Part-1B** | Final Generation Manifest | [Part-1B/evidence/final-generation/README.md](Part-1B/evidence/final-generation/README.md) | Manifest for final live evaluation run. |
| **Part-1B** | Final Harness Log | [Part-1B/evidence/final-generation/harness-log.md](Part-1B/evidence/final-generation/harness-log.md) | Final live evaluation transcript: 🟢 **PASS** across all dimensions. |
| **Part-1B** | Final Raw Results | [Part-1B/evidence/final-generation/eval-results.json](Part-1B/evidence/final-generation/eval-results.json) | Complete final JSON benchmark output. |
| **Part-1B** | Independent Revalidation Log | [Part-1B/evidence/revalidated-independent/harness-log.md](Part-1B/evidence/revalidated-independent/harness-log.md) | Decoupled re-validation run transcript (100% pass). |
| **Part-1B** | Independent Revalidation JSON | [Part-1B/evidence/revalidated-independent/eval-results.json](Part-1B/evidence/revalidated-independent/eval-results.json) | Decoupled re-validation JSON output. |
| **Part-1B** | Final Human Decision | [Part-1B/evidence/final-generation/harness-log.md#7-final-human-review-and-decision](Part-1B/evidence/final-generation/harness-log.md#7-final-human-review-and-decision) | Decision: **ACCEPT** (Signed: Prashant Bhattacharya). |

---

## 7. Continuous Integration (CI) Workflow

The automated CI pipeline is configured at [.github/workflows/ci.yml](.github/workflows/ci.yml).

### Pipeline Scope & Execution Boundary

```yaml
name: CI Validation Harness
on:
  push:
    branches: [ "main" ]
  pull_request:
    branches: [ "main" ]

jobs:
  validate-part-1a:
    name: "Part 1A: Expense Management Harness"
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.9", "3.10", "3.11"]
    defaults:
      run:
        working-directory: Part-1A
```

### Key Architectural Characteristics of the CI Workflow:

1. **Dedicated Part-1A Validation**:
   - CI executes strictly in `working-directory: Part-1A`.
   - Tests compatibility across Ubuntu runners using a matrix of **Python 3.9, 3.10, and 3.11**.
   - Executes the complete deterministic 4-gate sequence:
     1. `ruff check .` and `ruff format --check .` (Gate 1)
     2. `bandit -c pyproject.toml -r src/` (Gate 2)
     3. `pip-audit -r requirements.txt` (Gate 3)
     4. `pytest -v` (Gate 4)

2. **Why Part-1B is NOT Executed in GitHub Actions**:
   - **Runtime Constraints**: Part-1B requires Python 3.13 (`requires-python = ">=3.13"`).
   - **Security & Secret Isolation**: Live evaluations require a Groq Cloud API key. Running live evaluations in public or multi-tenant CI runners introduces credential exposure risks and rate-limiting failure modes.
   - **Determinism**: Part-1B's 81-test Pytest suite and live evaluation harness are engineered to run locally in isolated environments (`.venv313`), guaranteeing reproducibility without relying on cloud runner egress.

---

## 8. Known Limitations & External Dependencies

### Part-1A Limitations
1. **SQLite Concurrency**: SQLite file persistence (`expenses.db`) uses database-level locking during write transactions. It is designed for single-node development and MVP evaluation; production deployments require PostgreSQL or MySQL.
2. **Strict Currency Boundary**: Only INR (`DEFAULT_CURRENCY = "INR"`) is supported. Multi-currency conversions or forex rates are intentionally excluded by specification.
3. **Immutable Claims**: Submitted claims cannot be updated or deleted (`PUT`/`DELETE` return HTTP 405). Mistakes require a manager rejection followed by a new submission.
4. **Starlette Deprecation Notices**: Pytest session summaries emit non-fatal Starlette deprecation warnings regarding future migration from `HTTP_422_UNPROCESSABLE_ENTITY` to `HTTP_422_UNPROCESSABLE_CONTENT` and testclient HTTPX versioning. All 28 tests pass.
5. **Educational MVP Scope**: Accepted as a specification-compliant educational assignment MVP; does not constitute commercial enterprise-grade production certification.

### Part-1B Limitations
1. **External Cloud Inference Dependency**: Semantic code review relies on the external Groq Cloud API hosting `openai/gpt-oss-120b`. The service is subject to network availability, upstream rate limits, and provider outages.
2. **Observed Inference Latency**: The observed p95 evaluation latency is 8,852 ms (~8.9s). While well within the 15,000 ms ceiling, this makes the service suitable for pull-request or asynchronous reviews rather than blocking pre-commit git hooks.
3. **Payload Boundaries**: Single-file Python analysis is bounded at 1,000 lines and 65,536 UTF-8 bytes. Multi-file repository dependency graphs or non-Python languages are out of scope for this MVP.
4. **Subjective Confidence Scores**: Finding confidence values (0.0 to 1.0) represent model-generated heuristics rather than mathematically calibrated Bayesian probabilities.
5. **Runtime Prompt Version Default**: If `PROMPT_VERSION` is not explicitly set in `Part-1B/.env` or environment variables, the web service defaults to `v1.0.0` in telemetry. To use `v2.1.0` at runtime, configure `PROMPT_VERSION=v2.1.0`.
6. **Human-in-the-Loop Requirement**: Automated AI reviews supplement, but do not replace, human architectural peer review, dynamic testing, and runtime security monitoring.
