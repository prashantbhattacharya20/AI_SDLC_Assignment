# Technical Research & Architecture Decisions: Expense Management System (MVP)

**Feature**: Expense Management System (MVP)
**Branch**: `001-expense-management`
**Date**: 2026-11-18
**Status**: Completed

## 1. Executive Summary

This research document analyzes and establishes the concrete technical foundation for the Expense Management System (MVP). In alignment with the project constitution (`v2.0.0`), the system is designed as a deterministic FastAPI web service that implements modular component architecture, strict contract validation, test-first development, and structured observability without superfluous abstractions.

---

## 2. Technical Decisions & Rationales

### Decision 1: Application Framework & Web Stack
- **Decision**: Python 3.11+ with **FastAPI** and **Uvicorn**.
- **Rationale**:
  - Native integration with Pydantic v2 for deterministic data validation and schema serialization.
  - Automatic OpenAPI 3.1 generation providing immediate interface contracts.
  - Asynchronous and synchronous request handling with dependency injection for clean component decoupling.
- **Alternatives Considered**:
  - *Flask*: Rejected due to lack of native async support, manual OpenAPI integration, and boilerplate schema validation.
  - *Django / Django REST Framework*: Rejected as heavy-weight for an MVP web service; violates YAGNI by introducing unnecessary ORM/admin baggage.

### Decision 2: Data Persistence & Storage Layer
- **Decision**: **SQLite** via **SQLAlchemy 2.0** with explicit transactional isolation.
- **Rationale**:
  - Zero-configuration, zero-external-dependency embedded relational database ideal for deterministic local development, testing, and MVP deployment.
  - Full ACID compliance ensuring relational consistency and transaction isolation for financial status transitions.
  - SQLAlchemy 2.0 provides clean declarative models and query interfaces without breaking separation of concerns.
- **Alternatives Considered**:
  - *PostgreSQL*: Production-grade, but adds docker/network operational overhead for the MVP without immediate functional benefit. Can be swapped seamlessly via SQLAlchemy engine configuration later.
  - *In-Memory Dictionaries*: Rejected because financial auditability and state persistence require relational integrity and durability across server restarts.

### Decision 3: Currency & Decimal Precision
- **Decision**: **Python `decimal.Decimal`** mapped to SQLAlchemy `Numeric(12, 2)` and validated via Pydantic `condecimal(gt=0, decimal_places=2)`, with **INR (₹)** as the default currency.
- **Rationale**:
  - Floating-point representations (`float`) introduce binary rounding errors (e.g., `0.1 + 0.2 != 0.3`), which are unacceptable in financial applications.
  - Exact fixed-point arithmetic guarantees 100% deterministic calculation and balance verification in Indian Rupees (INR) with two decimal places (paise).
- **Alternatives Considered**:
  - *Integer Paise*: Storing amounts as integer paise (e.g., ₹10.50 -> 1050 paise) is viable, but requires repetitive conversions at API and reporting boundaries. `Decimal` provides high precision with direct human-readable JSON serialization.

### Decision 4: State Machine & Workflow Validation
- **Decision**: Encapsulated Domain State Machine inside `ExpenseService` with an explicit state transition table: `SUBMITTED` → `APPROVED` (Terminal) | `REJECTED` (Terminal).
- **Rationale**:
  - State machine rules are simple and deterministic:
    - Expenses are created directly in `SUBMITTED` status.
    - `SUBMITTED` → `APPROVED` (Terminal)
    - `SUBMITTED` → `REJECTED` (Terminal)
  - `APPROVED` and `REJECTED` are immutable terminal states; transitions backwards or edits raise `StateTransitionError` (HTTP 409 Conflict).
  - Update and delete operations are strictly omitted from the API scope per the approved MVP specification; submitted expenses cannot be modified or deleted.
  - Keeps workflow logic centralized, testable in isolation, and decoupled from HTTP routers.
- **Alternatives Considered**:
  - *Third-party state machine libraries (e.g., `transitions`)*: Rejected under Constitution Principle IV (YAGNI & dependency minimization); a simple Python enum transition map achieves the exact behavior with zero external dependencies.

### Decision 5: Authentication & Authorization Mock for MVP
- **Decision**: Header-based authentication simulation via FastAPI dependency (`X-User-Id` and `X-User-Role`), backed by seed user records.
- **Rationale**:
  - Avoids premature integration with external OAuth2/OIDC identity providers while fully validating role-based access control (RBAC) and self-approval prevention (`submitter_id != approver_id`).
  - Enables 100% deterministic automated testing of employee vs. manager permissions in unit and integration test suites.
- **Alternatives Considered**:
  - *Full JWT Auth with bcrypt*: Adds cryptographic key management and user signup flows that are outside the MVP scope defined in `spec.md`.

### Decision 6: Testing Strategy & Test Harness
- **Decision**: **Pytest** with `httpx.AsyncClient` / `TestClient`, enforcing Red-Green-Refactor TDD.
- **Rationale**:
  - Satisfies Constitution Principle I (TDD non-negotiable for deterministic systems).
  - Modular test directory layout separating unit tests (`tests/unit`), contract tests (`tests/contract`), and integration scenarios (`tests/integration`).
  - High test speed using in-memory or temporary SQLite databases for isolated test runs.
- **Alternatives Considered**:
  - *Standard `unittest`*: Less expressive fixtures and assertion introspection compared to Pytest.

---

## 3. Dependency Inventory

In adherence to Constitution Constraint "Dependency Minimization":
- `fastapi` (>=0.110.0): Core web API framework.
- `uvicorn[standard]` (>=0.28.0): ASGI server.
- `pydantic` (>=2.6.0): Data validation and contract modeling.
- `sqlalchemy` (>=2.0.0): Database ORM and relational mapping.
- `pytest` (>=8.0.0) [dev]: Test runner.
- `httpx` (>=0.27.0) [dev]: HTTP test client for FastAPI.
- `ruff` (>=0.3.0) [dev]: Fast linter and code formatter.
