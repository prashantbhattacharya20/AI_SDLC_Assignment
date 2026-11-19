"""Shared Pytest fixtures for Part 1B: AI Code Review Assistant."""

from typing import Any

import pytest

# ---------------------------------------------------------------------------
# Sample Code Snippets for Testing
# ---------------------------------------------------------------------------


@pytest.fixture
def clean_code_snippet() -> str:
    return 'def add(a: int, b: int) -> int:\n    """Return the sum of two integers."""\n    return a + b\n'


@pytest.fixture
def bug_code_snippet() -> str:
    return "def calculate_average(items: list) -> float:\n    return sum(items) / len(items)\n"


@pytest.fixture
def security_code_snippet() -> str:
    return "import os\ndef run_command(user_input: str) -> None:\n    os.system('echo ' + user_input)\n"


@pytest.fixture
def syntax_error_snippet() -> str:
    return "def broken_function(\n    return 42\n"


@pytest.fixture
def secret_code_snippet() -> str:
    return 'GROQ_API_KEY = "gsk_abcdef1234567890abcdef1234567890ab"\ndef connect():\n    pass\n'


# ---------------------------------------------------------------------------
# Canned LLM Findings & Responses
# ---------------------------------------------------------------------------


@pytest.fixture
def canned_finding_dict() -> dict[str, Any]:
    return {
        "id": "F001",
        "title": "Potential ZeroDivisionError",
        "category": "BUG",
        "severity": "HIGH",
        "start_line": 2,
        "end_line": 2,
        "description": "Empty list causes ZeroDivisionError when calculating length.",
        "recommendation": "Add a check for empty items list before division.",
        "confidence": 0.95,
    }


@pytest.fixture
def canned_llm_response(canned_finding_dict) -> dict[str, Any]:
    return {"findings": [canned_finding_dict]}


# ---------------------------------------------------------------------------
# Mock LLM Client
# ---------------------------------------------------------------------------


class MockLLMClient:
    """Mock implementation of LLMClient protocol for deterministic testing."""

    def __init__(self, response_payload: dict[str, Any] = None, side_effect: Exception = None):
        self.response_payload = response_payload or {"findings": []}
        self.side_effect = side_effect
        self.call_count = 0
        self.last_prompt = None

    async def generate_review(self, prompt: str) -> dict[str, Any]:
        self.call_count += 1
        self.last_prompt = prompt
        if self.side_effect:
            raise self.side_effect
        return self.response_payload


@pytest.fixture
def mock_llm_client(canned_llm_response) -> MockLLMClient:
    return MockLLMClient(response_payload=canned_llm_response)
