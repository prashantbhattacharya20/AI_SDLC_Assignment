<!--
SYNC IMPACT REPORT
==================
Version Change: 1.0.0 -> 2.0.0
Ratification Date: 2026-11-18
Last Amended Date: 2026-11-18

Modified Principles:
- II. Library-First & Modularity -> II. Modular Component Architecture (Replaced standalone library mandate with modular, independently testable components; prohibited unnecessary packages and premature abstractions).
- I. Test-First Development (TDD) -> Expanded testing mandates to explicitly address deterministic systems (Part 1A: Expense Management) and non-deterministic systems (Part 1B: AI Code Review Assistant).
- III. Contract & Integration Testing -> Refined for FastAPI Pydantic contracts and LLM structured output/tool contracts.
- IV. Observability & Simplicity (YAGNI) -> Enhanced with dual-context observability (financial transaction traces for Part 1A; model metadata, token usage, and latency for Part 1B).
- V. Spec-Driven Quality Gates -> Explicitly incorporated Clarify and Analyze phases into the development lifecycle.

Added/Refined Sections:
- Engineering Constraints & Standards: Removed mandatory CLI/text-protocol requirement; established FastAPI and API-first web service conventions; preserved security, secret management, and dependency hygiene.
- Development Workflow & Quality Gates: Grounded automated quality gates in proportionate GitHub Actions workflows matching project scope.

Removed Sections/Constraints:
- Mandatory standalone library requirement for every business feature (Principle II).
- Mandatory CLI/text-based protocol requirement (Engineering Constraints).

Follow-up TODOs:
- None
-->

# AI SDLC Framework Constitution

## Core Principles

### I. Test-First Development (TDD)
Test-driven development is strictly non-negotiable for all functional units across both deterministic and non-deterministic application domains.
- Engineers and AI agents MUST write automated test suites prior to writing implementation code.
- Test suites MUST be validated in a failing state (Red) before implementation commences.
- Implementation code MUST satisfy only the requirements needed to transition tests from failing to passing (Green), followed by disciplined refactoring.
- **Deterministic Systems (Part 1A: Expense Management System)**: MUST enforce exact assertion-based unit, integration, and regression test suites verifying business rules, state machines, expense status transitions, calculation accuracy, and relational persistence.
- **Non-Deterministic Systems (Part 1B: AI Code Review Assistant)**: MUST implement deterministic evaluation harnesses, snapshot fixtures, contract-level mocks, and boundary assertions (e.g., schema adherence of model outputs, fallback triggers, and evaluation heuristics) to maintain test-first rigor despite model stochasticity.
- Pull requests lacking automated tests corresponding to new or modified behavior MUST NOT be merged.
*Rationale*: Writing tests first guarantees verified requirements, prevents untested logic leaks, and ensures regressions are immediately caught during AI-assisted development.

### II. Modular Component Architecture
Business capabilities and features MUST be structured as cohesive, modular, and independently testable components rather than isolated standalone libraries.
- Components MUST maintain well-defined, explicit public interfaces (classes, functions, Pydantic schemas) with minimal coupling between domain concerns.
- Unnecessary packages, premature micro-libraries, and speculative abstraction layers MUST be avoided; components SHOULD reside cleanly within idiomatic application layouts (such as FastAPI project modules) unless distinct distribution is required.
- Each component MUST be independently testable via unit tests with mockable dependencies where necessary.
- Organizational-only indirection and circular dependencies are strictly forbidden.
*Rationale*: Modular component design isolates cognitive scope for developers and AI agents, enabling targeted reasoning and testability without incurring unnecessary packaging or dependency overhead.

### III. Contract & Integration Testing
Inter-component communication, web interfaces, and external boundaries MUST be governed by explicit contracts and schemas.
- **API & Domain Contracts**: FastAPI endpoints and internal service boundaries MUST define strict Pydantic schemas, response models, and HTTP status contracts adhering to OpenAPI standards.
- **AI/LLM Contracts**: Non-deterministic interfaces (such as AI Code Review tools and prompt outputs) MUST declare and validate strict output schemas (e.g., JSON Schema/structured output parsing), including resilient handling for malformed model outputs.
- Contract modifications MUST maintain backward compatibility or provide explicit version migration pathways.
- Automated integration test suites MUST validate end-to-end data flow, error handling, and component interactions under realistic conditions.
*Rationale*: Contract testing prevents drift across component boundaries, ensuring reliability in both deterministic business logic and multi-step AI-assisted pipelines.

### IV. Observability & Simplicity (YAGNI)
Software design MUST prioritize simplicity, maintainability, and active observability across all execution paths.
- Systems MUST emit structured, contextual logs (standard JSON or key-value format) across critical execution paths.
- **Context-Aware Tracing**:
  - Deterministic workflows (Part 1A) MUST include correlation IDs, entity IDs, and state change details in logs.
  - AI/LLM workflows (Part 1B) MUST capture model identifiers, token consumption, inference latency, prompt versions, and structured evaluation metrics, while strictly redacting sensitive code or PII.
- Engineers and agents MUST adhere strictly to YAGNI ("You Aren't Gonna Need It")—no speculative features, superfluous configuration options, or premature architectural complexity.
- Code readability, standard Python/FastAPI idioms, and explicit control flows MUST take precedence over clever or opaque abstractions.
*Rationale*: Simple code combined with structured observability shortens debugging cycles, lowers maintenance cost, and minimizes hallucinations during AI-assisted refactoring.

### V. Spec-Driven Quality Gates
Feature delivery MUST strictly follow specification-driven lifecycle phases, incorporating upfront refinement before code execution.
- Work MUST proceed through the defined Spec-Driven Development stages:
  1. **Specify**: Define core feature scope, user stories, and acceptance criteria in `spec.md`.
  2. **Clarify**: Interactively resolve ambiguities, missing edge cases, and underspecified requirements to establish crisp boundaries before technical planning.
  3. **Plan**: Formulate architectural blueprints, component contracts, and technical strategies in `plan.md`.
  4. **Tasks**: Break down the validated plan into actionable, dependency-ordered work items in `tasks.md`.
  5. **Analyze**: Perform non-destructive cross-artifact consistency and quality analysis across `spec.md`, `plan.md`, and `tasks.md` to validate alignment, detect contradictions, and catch gaps before code execution.
  6. **Implement**: Execute implementation strictly guided by task definitions with continuous test-driven verification.
- Code changes MUST trace directly to an explicit task item within the active specification plan; untracked or ad-hoc modifications are prohibited.
- Verification gates MUST be executed and passed at each phase boundary before proceeding to downstream stages.
*Rationale*: Systematic progression through Clarify, Plan, Tasks, and Analyze phases ensures cross-artifact consistency, prevents scope drift, and catches architectural defects before implementation.

## Engineering Constraints & Standards

All software artifacts within the framework MUST comply with the following architectural and security standards:
- **API-First & FastAPI Standards**: Applications are built as modern FastAPI web services. Endpoints, request/response models, and error responses MUST adhere to OpenAPI specifications, Pydantic validation, and RESTful conventions. Universal CLI interfaces are NOT required.
- **Dependency Minimization**: Dependencies MUST be audited for necessity, active maintenance, and security vulnerabilities. Unnecessary third-party packages and speculative wrappers are prohibited.
- **Security & Secret Hygiene**: Secrets, API keys, credentials, and sensitive tokens MUST NEVER be committed to version control. Configuration MUST be externalized via environment variables (e.g., `pydantic-settings` or `.env` files with git exclusion).
- **Static Analysis & Code Quality**: Code MUST conform to standard linting (e.g., Ruff) and static type checking rules without unhandled exceptions or disabled safety checks.

## Development Workflow & Quality Gates

The development lifecycle enforces automated and peer review checkpoints proportionate to project scope:
1. **Specification Alignment**: Every pull request MUST reference its governing specification or feature requirement artifact.
2. **Proportionate Automated CI/CD (GitHub Actions)**:
   - Automated quality gates MUST be implemented via lightweight, reliable GitHub Actions workflows proportionate to the repository scope.
   - Workflows MUST execute automated linting, static type verification, unit tests, and contract checks on active branches and pull requests.
   - CI workflows SHOULD remain focused and fast, avoiding redundant or over-engineered stages while guaranteeing baseline quality.
3. **Review & Gate Enforcement**: Merges require passing CI checks, up-to-date documentation, test coverage for new/modified behaviors, and verified alignment with constitution principles.

## Governance

This constitution serves as the foundational authority governing all development, architecture, and review processes within the repository.
- **Supremacy**: The rules herein supersede informal team conventions, ad-hoc practices, and conflicting legacy documentation.
- **Compliance in Code Review**: All pull requests, automated agent reviews, and peer evaluations MUST explicitly verify compliance with these core principles. Any introduced complexity or exception MUST be formally justified.
- **Amendment Procedure**: Amendments to this constitution require a formal proposal, impact analysis, version increment, and consensus approval.
- **Versioning Policy**: Semantic versioning (SemVer) applies to this constitution:
  - **MAJOR (`X.0.0`)**: Backward-incompatible governance changes, removal or fundamental redefinition of core principles.
  - **MINOR (`X.Y.0`)**: Addition of new principles, new sections, or materially expanded guidelines.
  - **PATCH (`X.Y.Z`)**: Clarifications, non-semantic wording refinements, and typo corrections.

**Version**: 2.0.0 | **Ratified**: 2026-11-18 | **Last Amended**: 2026-11-18
