"""Deterministic Python AST syntax checker.

Cites: Part-1B/specs/001-code-review-assistant/plan.md (Layer 3: Core Service Layer)
"""

import ast

from src.schemas.enums import DefectCategory, SeverityLevel
from src.schemas.response import ReviewFinding


class SyntaxChecker:
    """Parses Python source code to detect syntax errors before LLM dispatch."""

    def check_syntax(self, code: str) -> ReviewFinding | None:
        """Parse source code with Python AST. Returns CRITICAL BUG finding if SyntaxError occurs."""
        try:
            ast.parse(code)
            return None
        except SyntaxError as e:
            line_no = e.lineno if e.lineno and e.lineno > 0 else 1
            return ReviewFinding(
                id="AST-SYNTAX-001",
                title=f"Python Syntax Error: {e.msg}",
                category=DefectCategory.BUG,
                severity=SeverityLevel.CRITICAL,
                start_line=line_no,
                end_line=line_no,
                description=f"Fatal Python syntax error prevents execution: '{e.msg}' at line {line_no}.",
                recommendation="Correct the invalid Python syntax before submitting for semantic code review.",
                confidence=1.0,
            )
