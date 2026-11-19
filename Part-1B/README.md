# Part 1B: AI Code Review Assistant

**Course**: BITS Pilani WILP<br>
**Assignment**: Assignment 1 (Spec-Driven Development & Harness Engineering)<br>
**Author**: Prashant Bhattacharya<br>
**Status**: **Fully Implemented & Empirically Verified (100% Quality Gates Passing)**<br>
**Runtime**: Python 3.13.9 (`.venv313`) | **Primary Provider**: Groq (`openai/gpt-oss-120b`)

---

## 1. Overview

Part 1B implements an **AI Code Review Assistant** that leverages Large Language Models (LLMs) via the Groq API to perform automated static code analysis, identifying:
- **Bugs**: Logic defects, unhandled exceptions, and edge-case errors.
- **Security Vulnerabilities**: Injection risks, exposed credentials, and OWASP antipatterns.
- **Performance Bottlenecks**: Inefficient algorithms and redundant compute.
- **Maintainability Issues**: Complex control flows, cognitive debt, and code smells.

The assistant pairs non-deterministic LLM analysis with strict **deterministic pre- and post-validation gates**:
1. **Pre-Validation**: Input language validation (strictly Python), dual payload limits (max 1,000 lines and 65,536 UTF-8 bytes), pattern-based secret screening (immediate HTTP 422 rejection), and deterministic Python AST syntax checking (intercepts fatal syntax errors locally with a `CRITICAL` `BUG` finding without calling Groq).
2. **Model Integration**: Decoupled `LLMClient` protocol utilizing official Groq SDK with native JSON mode and bounded retry handling (max 2 retries with exponential backoff ~1s and ~2s for transient network, rate limits, or recoverable schema failures; permanent auth/config errors fail immediately; exhausted retries return HTTP 502).
3. **Post-Validation & Invariants**: Strict Pydantic v2 schema enforcement, line number boundary validation (`1 <= start_line <= end_line <= total_lines`), finding deduplication, and automated release quality gating (`FAIL` if any `CRITICAL` or `HIGH` findings exist; `PASS` otherwise).

---

## 2. Directory Structure

This sub-project maintains dedicated isolation from Part 1A in compliance with Section 4.9 and Section 6 of the assignment specification:

```text
Part-1B/
├── README.md                              # This navigation & execution guide
├── pyproject.toml                         # Tooling configuration (Ruff, Bandit, Pytest) [Phase 1]
├── requirements.txt                       # Python 3.13 dependencies [Phase 1]
│
├── .specify/                              # Independent Spec Kit project
│   ├── memory/
│   │   └── constitution.md                # Project Constitution v1.1.1 (TDD, EDD, Invariants)
│   ├── templates/                         # Spec Kit markdown templates
│   ├── scripts/                           # Spec Kit bash automation scripts
│   └── workflows/                         # Workflow registry definitions
│
├── specs/                                 # Feature specifications & planning artifacts
│   └── 001-code-review-assistant/
│       ├── spec.md                        # Feature specification with 5/5 ratified clarifications
│       ├── plan.md                        # Architectural implementation plan & constitution gates
│       ├── research.md                    # Phase 0 architectural decisions & trade-offs
│       ├── data-model.md                  # Domain schemas, invariants, & telemetry entities
│       ├── contracts/
│       │   └── code-review-api.yaml       # OpenAPI 3.1 web service contract
│       ├── quickstart.md                  # Runnable end-to-end validation scenarios
│       ├── checklists/
│       │   └── requirements.md            # 16/16 specification quality checklist
│       └── tasks.md                       # Ordered, dependency-tracked implementation tasks
│
├── src/                                   # Application source code [Implemented & Tested]
│   ├── main.py                            # FastAPI entrypoint, exception handlers, CORS
│   ├── config.py                          # Pydantic Settings environment configuration
│   ├── schemas/                           # Pydantic v2 request, response, enum, error schemas
│   ├── services/                          # Secret scanner, AST syntax checker, review orchestrator
│   ├── llm/                               # Groq client adapter & versioned prompt templates
│   └── api/v1/                            # REST route handlers (/review, /health)
│
├── prompts/                               # Versioned analysis prompts [Phase 2 & 6]
│   ├── review_system_prompt_v1.txt        # Baseline system prompt (v1.0.0)
│   ├── review_system_prompt_v2.txt        # Intermediate prompt (v2.0.0)
│   ├── review_system_prompt_v2_1.txt      # Final active prompt (v2.1.0)
│   └── README.md                          # Versioned prompts manifest
│
├── tests/                                 # Automated test suite (Strict TDD) [Phases 2-5]
│   ├── conftest.py                        # Shared test fixtures (mock Groq client, sample snippets)
│   ├── unit/                              # Unit tests (schemas, secrets, AST syntax, prompt, regression)
│   ├── contract/                          # OpenAPI 3.1 contract verification tests
│   └── integration/                       # FastAPI TestClient mocked end-to-end tests
│
├── evals/                                 # Evaluation benchmark dataset & runner [Phase 6]
│   ├── config.json                        # Frozen acceptance thresholds & evaluation config
│   ├── dataset.json                       # Ground-truth evaluation dataset (18 verified cases)
│   ├── runner.py                          # Benchmark harness execution engine
│   └── metrics.py                         # Evaluation metric scorers across 3 dimensions
│
├── .harness/                              # Evaluation harness shell runner [Phase 6]
│   └── run-evals.sh                       # Shell runner script for live evaluations
│
└── evidence/                              # Benchmark execution logs & manifests [Phase 6]
    ├── initial-generation/                # Baseline prompt evaluation results (v1.0.0)
    │   ├── eval-results.json              # Baseline raw outputs and dimension scores
    │   └── harness-log.md                 # Baseline execution transcript
    ├── v2.0.0-generation/                 # Intermediate prompt evaluation results (v2.0.0)
    │   ├── eval-results.json              # v2.0.0 raw outputs and dimension scores
    │   └── harness-log.md                 # v2.0.0 execution transcript
    └── final-generation/                  # Final live prompt evaluation results (v2.1.0 - PASS)
        ├── eval-results.json              # Final raw outputs and dimension scores
        └── harness-log.md                 # Final execution transcript
```

---

## 3. Spec Kit Artifact Manifest

All planning and governance artifacts have been produced, reviewed, and verified via `/speckit-analyze` prior to code generation:

- **Constitution**: [`Part-1B/.specify/memory/constitution.md`](.specify/memory/constitution.md) (Version 1.1.1)
- **Feature Specification**: [`Part-1B/specs/001-code-review-assistant/spec.md`](specs/001-code-review-assistant/spec.md) (Includes 5/5 ratified clarification points)
- **Quality Checklist**: [`Part-1B/specs/001-code-review-assistant/checklists/requirements.md`](specs/001-code-review-assistant/checklists/requirements.md) (16/16 items passing)
- **Implementation Plan**: [`Part-1B/specs/001-code-review-assistant/plan.md`](specs/001-code-review-assistant/plan.md) (Gates passed, zero complexity violations)
- **Architectural Research**: [`Part-1B/specs/001-code-review-assistant/research.md`](specs/001-code-review-assistant/research.md) (All 9 decision points resolved)
- **Data Model & Invariants**: [`Part-1B/specs/001-code-review-assistant/data-model.md`](specs/001-code-review-assistant/data-model.md) (All 30 constrained fields cited)
- **API Contract**: [`Part-1B/specs/001-code-review-assistant/contracts/code-review-api.yaml`](specs/001-code-review-assistant/contracts/code-review-api.yaml) (OpenAPI 3.1 conforming)
- **Validation Guide**: [`Part-1B/specs/001-code-review-assistant/quickstart.md`](specs/001-code-review-assistant/quickstart.md) (6 end-to-end curl scenarios)
- **Tasks Breakdown**: [`Part-1B/specs/001-code-review-assistant/tasks.md`](specs/001-code-review-assistant/tasks.md) (54 tasks, strict TDD & EDD dependencies)

---

## 4. Environment Setup & Execution Instructions

### 4.1 Prerequisites & Virtual Environment

The project requires **Python 3.13.9** using the active root `.venv313` virtual environment:

```bash
# From repository root:
source .venv313/bin/activate

# Verify Python version:
python --version  # Must output Python 3.13.9

# Navigate to Part-1B:
cd Part-1B
```

### 4.2 Configuration

Create `.env` inside `Part-1B/` (automatically excluded by `.gitignore`):

```bash
GROQ_API_KEY=gsk_your_groq_api_key_here
GROQ_MODEL=openai/gpt-oss-120b
ENVIRONMENT=development
```

### 4.3 Running Deterministic Tests

Per Constitution Principle I, all unit, contract, and integration tests use mocked Groq responses and execute fully offline without requiring a live API key:

```bash
# Run complete test suite:
pytest -v

# Run unit tests:
pytest tests/unit/ -v

# Run OpenAPI 3.1 contract tests:
pytest tests/contract/ -v

# Run mocked integration tests:
pytest tests/integration/ -v
```

### 4.4 Running the Local FastAPI Service

```bash
uvicorn src.main:app --host 127.0.0.1 --port 8000 --reload
```
Interactive OpenAPI documentation is accessible at `http://127.0.0.1:8000/docs`.

### 4.5 Running the Evaluation Benchmark Harness

Live model evaluations execute against `evals/dataset.json` (>=15 verified cases across 6 scenarios) using the frozen thresholds in `evals/config.json`:

```bash
# Ensure live GROQ_API_KEY is exported:
export GROQ_API_KEY="gsk_your_live_key"

# Run evaluation harness:
./.harness/run-evals.sh

# Or directly via Python runner:
python -m evals.runner --dataset evals/dataset.json --output evidence/final-generation/eval-results.json
```

---

## 5. Evaluation Benchmarks & Pre-Set Acceptance Thresholds

Evaluation independently assesses three distinct dimensions:
1. **Dimension A (Schema Adherence)**: 100% of outputs must conform to Pydantic/OpenAPI schemas.
2. **Dimension B (Deterministic Invariants)**: 100% of finding line numbers within bounds, non-empty fields, valid deduplication.
3. **Dimension C (Semantic Quality)**:
   - **Precision**: >= 80%
   - **Recall**: >= 80%
   - **F1 Score**: >= 80%
   - **False-Positive Rate**: <= 15%

All baseline (v1.0.0) and final (optimized) evaluation evidence will be preserved in `evidence/initial-generation/` and `evidence/final-generation/`.
