"""Deterministic pattern-based secret scanner for pre-validation gating.

Cites: Part-1B/specs/001-code-review-assistant/plan.md (Layer 3: Core Service Layer)
"""

import re
from typing import NamedTuple


class SecretDetection(NamedTuple):
    """Metadata regarding a detected secret token."""

    pattern_name: str
    line_number: int

    def masked_description(self) -> str:
        """Return safe description without exposing any secret tokens."""
        return f"Exposed credential pattern ({self.pattern_name}) detected at line {self.line_number}"


class SecretScanner:
    """Detects high-entropy credentials, tokens, and private keys via regex patterns."""

    PATTERNS = [
        ("Groq API Key", re.compile(r"\bgsk_[A-Za-z0-9]{24,}\b")),
        ("OpenAI API Key", re.compile(r"\bsk-[A-Za-z0-9]{20,}\b")),
        ("GitHub Personal Access Token", re.compile(r"\b(gh[pousr]_[A-Za-z0-9_]{36,}|github_pat_[A-Za-z0-9_]{22,})\b")),
        ("AWS Access Key", re.compile(r"\b(AKIA|ABIA|ACCA|ASIA)[0-9A-Z]{16}\b")),
        ("Private Key Header", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
        (
            "Generic High-Entropy Credential",
            re.compile(r"""(?i)(?:api_key|secret_key|client_secret|auth_token)\s*=\s*['"][A-Za-z0-9_\-]{20,}['"]"""),
        ),
    ]

    def scan(self, code: str) -> list[SecretDetection]:
        """Scan code line-by-line for secret patterns and return detections."""
        detections: list[SecretDetection] = []
        lines = code.splitlines()

        for idx, line in enumerate(lines, start=1):
            for name, pattern in self.PATTERNS:
                if pattern.search(line):
                    detections.append(SecretDetection(pattern_name=name, line_number=idx))
                    break  # Record one detection per line

        return detections
