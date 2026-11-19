# Part 1B: Automated Test Suite Manifest

This directory houses the comprehensive automated test suite for the AI Code Review Assistant.

## Test Organization (Strict TDD)

1. `conftest.py`: Shared pytest fixtures, including mock Groq LLM client, mock responses, and sample code snippets (Phase 1 - T006).
2. `unit/`: Granular unit tests validating isolated components:
   - `test_config.py`: Settings loading and validation (Phase 1 - T003).
   - `test_schemas.py`: Pydantic schema validation and invariant rejection (Phase 1 - T005).
   - `test_secret_scanner.py`: Secret detection, zero Groq invocation, credential privacy (Phase 2 - T017).
   - `test_ast_syntax_checker.py`: AST parsing, error interception, non-Python rejection (Phase 2 - T019).
   - `test_llm_client.py`: Mocked Groq client, retry logic, timeout handling (Phase 2 - T007).
   - `test_prompt_rendering.py`: Prompt template loading and variable substitution (Phase 2 - T009).
   - `test_review_orchestrator.py`: Review workflow orchestration and invariant enforcement (Phase 3 - T021).
   - `test_eval_metrics.py`: Schema adherence, invariant compliance, precision/recall scorers (Phase 6 - T042).
   - `test_eval_runner.py`: Benchmark runner, threshold evaluation, serialization (Phase 6 - T043).
3. `contract/`: API contract conformance tests:
   - `test_openapi_contract.py`: Validates responses and status codes against `code-review-api.yaml` (Phase 2 - T014).
4. `integration/`: End-to-end integration tests:
   - `test_api_endpoints.py`: FastAPI TestClient tests for `/api/v1/health` and `/api/v1/review` (Phase 2 - T014, Phase 3 - T027).
   - `test_quickstart.py`: Automated execution of all 6 scenarios in `quickstart.md` (Phase 5 - T039).

*Implementation Note: Tests are committed and verified FAILING before corresponding implementation tasks are executed.*
