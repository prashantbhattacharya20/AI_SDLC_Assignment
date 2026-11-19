"""Domain enumerations for the AI Code Review Assistant.

Cites: Part-1B/specs/001-code-review-assistant/data-model.md
"""

from enum import StrEnum


class DefectCategory(StrEnum):
    """Categorization of detected code defects.

    Cites: data-model.md (DefectCategory)
    """

    BUG = "BUG"
    SECURITY = "SECURITY"
    PERFORMANCE = "PERFORMANCE"
    MAINTAINABILITY = "MAINTAINABILITY"


class SeverityLevel(StrEnum):
    """Severity level of detected defects.

    Cites: data-model.md (SeverityLevel)
    """

    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


class ReviewStatus(StrEnum):
    """Aggregated status of the review based on deterministic gating rules.

    Cites: data-model.md (ReviewStatus)
    """

    PASS = "PASS"  # nosec B105
    FAIL = "FAIL"
