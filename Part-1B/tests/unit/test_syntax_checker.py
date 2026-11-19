"""Unit tests for deterministic Python AST syntax checker (T026).

Verifies local CRITICAL BUG finding generation without invoking the Groq LLM client.
"""


def test_syntax_checker_clean_python():
    from src.services.syntax_checker import SyntaxChecker

    checker = SyntaxChecker()
    code = "def valid_func(x: int) -> int:\n    return x + 1\n"
    finding = checker.check_syntax(code)
    assert finding is None


def test_syntax_checker_detects_syntax_error():
    from src.schemas.enums import DefectCategory, SeverityLevel
    from src.services.syntax_checker import SyntaxChecker

    checker = SyntaxChecker()
    code = "def broken_func(\n    return 42\n"
    finding = checker.check_syntax(code)

    assert finding is not None
    assert finding.category == DefectCategory.BUG
    assert finding.severity == SeverityLevel.CRITICAL
    assert finding.start_line in [1, 2]
    assert finding.confidence == 1.0
    assert "SyntaxError" in finding.title or "Syntax Error" in finding.title
    assert "syntax error" in finding.description.lower()
