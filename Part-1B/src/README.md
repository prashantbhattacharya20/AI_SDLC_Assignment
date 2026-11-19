# Part 1B: Application Source Code Manifest

This directory will contain the implementation of the AI Code Review Assistant service.

## Architectural Layers (Five-Tier Architecture)

1. `main.py`: FastAPI application entrypoint, CORS configuration, and structured exception handlers (Phase 2 - T015).
2. `config.py`: Pydantic Settings environment configuration (`GROQ_API_KEY`, `APP_ENV`, etc.) (Phase 1 - T004).
3. `schemas/`: Pydantic v2 data models for requests, findings, summary, telemetry, and structured errors (Phase 1 - T008).
4. `services/`: Core deterministic business logic:
   - `secret_scanner.py`: High-entropy and pattern-based secret detection (Phase 2 - T020).
   - `ast_syntax_checker.py`: Deterministic Python AST parsing and syntax error interception (Phase 2 - T022).
   - `review_orchestrator.py`: Multi-stage review coordination and invariant post-processing (Phase 3 - T024).
5. `llm/`: Groq LLM client adapter with native JSON mode and bounded exponential backoff retry handler (Phase 2 - T010, T012).
6. `api/v1/`: HTTP route handlers:
   - `review.py`: POST `/api/v1/review` code review endpoint (Phase 3 - T028).
   - `health.py`: GET `/api/v1/health` readiness and liveness check (Phase 2 - T016).

*Implementation Note: All modules will be developed strictly test-first (TDD) according to `tasks.md`.*
