# Implementation Plan: Expense Management System (MVP)

**Branch**: `001-expense-management` | **Date**: 2026-11-18 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from [specs/001-expense-management/spec.md](spec.md)

## Summary

Build a deterministic FastAPI web service providing an end-to-end expense management system for submitting, reviewing, approving, and tracking employee business expenses (MVP scope). The system enforces strict two-decimal currency precision in Indian Rupees (INR - ₹), discrete state machine transitions (`SUBMITTED` → `APPROVED` | `REJECTED`), immutable terminal states, self-approval prevention, role-based authorization, and comprehensive audit trail logging. Architecture follows modular component design using Pydantic v2 schemas, SQLAlchemy 2.0 with SQLite, and Pytest test-driven verification.

## Technical Context

**Language/Version**: Python 3.11+

**Primary Dependencies**: FastAPI (>=0.110.0), Pydantic v2 (>=2.6.0), SQLAlchemy (>=2.0.0), Uvicorn (>=0.28.0)

**Storage**: SQLite with SQLAlchemy 2.0 relational persistence and explicit transaction isolation

**Testing**: Pytest (>=8.0.0), pytest-asyncio, HTTPX TestClient

**Target Platform**: Cross-platform server (Linux / macOS / containerized)

**Project Type**: Web service (REST API)

**Performance Goals**: Sub-100ms p95 latency on all endpoints; immediate consistency and ACID persistence for financial state transitions

**Constraints**: Default currency INR (₹), strict two-decimal precision (`Decimal`), terminal state immutability, update and delete operations omitted per approved MVP scope, zero external cloud dependencies for MVP, secrets externalized

**Scale/Scope**: MVP Core Scope: 3 user journeys (submit, approve/reject, history), 4 core entities, 5 REST endpoints

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Principle I: Test-First Development (TDD)**: **PASSED** — Automated unit, contract, and integration tests MUST be authored and confirmed failing before implementation code is written. Exact assertion testing verifies financial precision (INR with paise), state machine transitions, and validation rules.
- **Principle II: Modular Component Architecture**: **PASSED** — Features organized into cohesive, modular components (`routers/`, `services/`, `models/`, `schemas/`) within an idiomatic FastAPI project layout. No unnecessary packages or speculative abstraction layers.
- **Principle III: Contract & Integration Testing**: **PASSED** — OpenAPI 3.1 contract formally documented in [contracts/expenses-api.yaml](contracts/expenses-api.yaml). Strict Pydantic v2 schema validation for all request/response models. Automated contract tests enforce schema adherence.
- **Principle IV: Observability & Simplicity (YAGNI)**: **PASSED** — Structured logging with correlation IDs on all state transitions; minimal external dependencies; single-level approval hierarchy for MVP without premature multi-tier complexity.
- **Principle V: Spec-Driven Quality Gates**: **PASSED** — Linear lifecycle strictly enforced: Specify (`spec.md`) → Clarify (`spec.md`) → Plan (`plan.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md`). Next stages: Tasks (`tasks.md`) → Analyze → Implement.
- **Engineering Constraints & Standards**: **PASSED** — API-first modern FastAPI web service; CLI protocol not mandated; secrets externalized; dependency minimization audited.
- **Development Workflow & CI/CD**: **PASSED** — Proportionate GitHub Actions quality gates (Ruff linting, static type verification, Pytest suites).

## Project Structure

### Documentation (this feature)

```text
specs/001-expense-management/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── contracts/           # Phase 1 output (/speckit-plan command)
│   └── expenses-api.yaml
└── tasks.md             # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

### Source Code (repository root)

```text
src/
├── __init__.py
├── main.py              # FastAPI app initialization, exception handlers, router mounts
├── config.py            # Environment settings via Pydantic Settings
├── database.py          # SQLAlchemy engine, session maker, base model
├── models/              # SQLAlchemy ORM models
│   ├── __init__.py
│   ├── user.py          # User entity & role definitions
│   ├── expense.py       # Expense & ApprovalAction entities
│   └── audit.py         # AuditLogEntry entity
├── schemas/             # Pydantic v2 request/response contracts & enums
│   ├── __init__.py
│   ├── common.py        # Enums (ExpenseStatus, ExpenseCategory, UserRole)
│   ├── expense.py       # ExpenseCreate, ExpenseResponse
│   └── approval.py      # ApprovalRequest, RejectionRequest, AuditLogResponse
├── services/            # Pure business logic, state machine, and authorization checks
│   ├── __init__.py
│   ├── expense_service.py
│   └── audit_service.py
└── api/                 # FastAPI routers & dependency injection
    ├── __init__.py
    ├── deps.py          # Auth simulation dependencies (X-User-Id, X-User-Role)
    └── v1/
        ├── __init__.py
        └── expenses.py  # REST endpoints for expense operations

tests/
├── conftest.py          # Shared fixtures (in-memory SQLite session, test client, seed users)
├── unit/                # Unit tests for domain models, validation, and state machine
│   ├── test_models.py
│   ├── test_schemas.py
│   └── test_expense_service.py
├── contract/            # Contract verification against OpenAPI schemas
│   └── test_openapi_contract.py
└── integration/         # End-to-end API lifecycle scenarios
    ├── test_expense_lifecycle.py
    └── test_authorization.py
```

**Structure Decision**: Selected single-project modular architecture conforming to FastAPI conventions and Constitution Principle II. Avoids micro-packages or premature sub-projects while maintaining strict separation of concerns between schemas, ORM models, business services, and HTTP routers.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

*Zero violations.* Design strictly adheres to constitution principles and YAGNI simplicity.
