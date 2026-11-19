# AI SDLC Assignment Repository

**Course**: BITS Pilani WILP  
**Assignment**: Assignment 1 (AI-Assisted Software Development Life Cycle)  
**Author**: Prashant Bhattacharya  

---

## 1. Repository Overview

This repository contains the deliverables for Assignment 1, organized into two dedicated and isolated sub-projects following the required submission architecture:

```text
AI_SDLC_Assignment/
├── README.md                              # Repository overview and navigation (this file)
├── .gitignore                             # Universal repository ignore rules
├── .github/
│   └── workflows/
│       └── ci.yml                         # Automated multi-gate CI validation pipeline
│
├── Part-1A/                               # Expense Management System (Completed)
│   ├── .specify/                          # Spec Kit governance & Constitution v2.0.0
│   ├── specs/                             # Specifications, plans, data model, tasks
│   ├── src/                               # FastAPI deterministic application code
│   ├── tests/                             # Contract, integration, and quickstart tests
│   ├── .harness/                          # Deterministic validation harness runner
│   ├── evidence/                          # Harness logs, raw scanner output, manifests
│   ├── pyproject.toml                     # Tooling configuration (Ruff, Bandit, Pytest)
│   └── requirements.txt                   # Part 1A dependencies
│
└── Part-1B/                               # AI Code Review Assistant (Under Development)
    ├── .specify/                          # Independent Spec Kit project
    ├── specs/                             # Part 1B specifications (to be generated)
    ├── src/                               # Code review engine & LLM integration (pending)
    ├── prompts/                           # Versioned analysis prompts (pending)
    ├── tests/                             # Test suite (pending)
    ├── evals/                             # Evaluation dataset & benchmarks (pending)
    ├── .harness/                          # Evaluation harness (pending)
    └── evidence/                          # Evaluation results & evidence log (pending)
```

---

## 2. Part 1A: Expense Management System (MVP)

- **Status**: **Completed & Fully Validated (Accepted)**
- **Architecture**: Deterministic FastAPI web service with SQLite persistence via SQLAlchemy 2.0 and Pydantic v2.
- **Currency Standard**: Strict **INR (₹)** with paise precision (`Decimal(12, 2)`).
- **Core Endpoints**: 5 strictly scoped endpoints (Submit, List/Filter, Detail with Audit Trail, Approve, Reject). Update and delete operations are omitted; submitted claims are immutable.
- **Validation Harness Gates**:
  1. **Ruff**: Linting and formatting checks (`ruff check .`, `ruff format --check .`) — *All checks passed, 51 files formatted*.
  2. **Bandit SAST**: Static application security testing (`bandit -c pyproject.toml -r src/`) — *656 lines scanned, 0 findings across all severity and confidence levels*.
  3. **pip-audit SCA**: Dependency vulnerability scanning (`pip-audit -r requirements.txt`) — *No known vulnerabilities found under Python 3.13.9*.
  4. **Pytest**: Automated test suite (`pytest -v`) — *28 passed, 0 failed, 9 Starlette deprecation warnings in 0.19s*.
- **Documentation & Evidence**:
  - Implementation Plan: [Part-1A/specs/001-expense-management/plan.md](Part-1A/specs/001-expense-management/plan.md)
  - API Contract: [Part-1A/specs/001-expense-management/contracts/expenses-api.yaml](Part-1A/specs/001-expense-management/contracts/expenses-api.yaml)
  - Validation Evidence Log: [Part-1A/evidence/harness-log.md](Part-1A/evidence/harness-log.md)
  - Raw Scanner Output: [Part-1A/evidence/harness-results/python313-rerun-evidence.txt](Part-1A/evidence/harness-results/python313-rerun-evidence.txt)

### Running Part 1A Locally

```bash
# From repository root:
source .venv313/bin/activate

# Execute the complete deterministic harness:
cd Part-1A
./.harness/run-harness.sh

# Or run tests directly:
pytest -v
```

---

## 3. Part 1B: AI Code Review Assistant

- **Status**: **Fully Implemented & Empirically Verified (100% Quality Gates Passing)**
- **Overview**: An LLM-powered Code Review Assistant designed to analyze source code and produce structured evaluation findings covering bugs, security vulnerabilities, performance bottlenecks, and maintainability issues.
- **Development Lifecycle**: Developed through the complete Spec-Driven Development (SDD) workflow using an isolated Spec Kit instance (`Part-1B/.specify/`).
- **Completed Governance & Planning Deliverables**:
  - Independent Constitution v1.1.1 in [Part-1B/.specify/memory/constitution.md](Part-1B/.specify/memory/constitution.md)
  - Feature Specification (5/5 ratified clarifications) in [Part-1B/specs/001-code-review-assistant/spec.md](Part-1B/specs/001-code-review-assistant/spec.md)
  - Quality Checklist (16/16 passed) in [Part-1B/specs/001-code-review-assistant/checklists/requirements.md](Part-1B/specs/001-code-review-assistant/checklists/requirements.md)
  - Architectural Implementation Plan in [Part-1B/specs/001-code-review-assistant/plan.md](Part-1B/specs/001-code-review-assistant/plan.md)
  - Architectural Research & Decisions in [Part-1B/specs/001-code-review-assistant/research.md](Part-1B/specs/001-code-review-assistant/research.md)
  - Domain Data Model in [Part-1B/specs/001-code-review-assistant/data-model.md](Part-1B/specs/001-code-review-assistant/data-model.md)
  - OpenAPI 3.1 Contract in [Part-1B/specs/001-code-review-assistant/contracts/code-review-api.yaml](Part-1B/specs/001-code-review-assistant/contracts/code-review-api.yaml)
  - Quickstart Verification Scenarios in [Part-1B/specs/001-code-review-assistant/quickstart.md](Part-1B/specs/001-code-review-assistant/quickstart.md)
  - Strict TDD & EDD Implementation Task Breakdown (54 tasks) in [Part-1B/specs/001-code-review-assistant/tasks.md](Part-1B/specs/001-code-review-assistant/tasks.md)
- **Delivered System Architecture & Evidence**:
  - `Part-1B/src/` (FastAPI application with 5 service layers)
  - `Part-1B/prompts/` (versioned prompt templates: v1.0.0, v2.0.0, v2.1.0)
  - `Part-1B/tests/` (66 unit, contract, integration, and regression tests passing)
  - `Part-1B/evals/` (18-case ground-truth dataset.json & frozen thresholds)
  - `Part-1B/.harness/` (evaluators & benchmark runner)
  - `Part-1B/evidence/` (baseline, v2.0.0 intermediate, and v2.1.0 passing evidence)

---

## 4. Continuous Integration (CI)

A centralized GitHub Actions workflow is maintained at [.github/workflows/ci.yml](.github/workflows/ci.yml). It executes the complete four-gate deterministic harness for Part 1A in dedicated working-directory isolation, ensuring reproducibility across Ubuntu Linux environments.
