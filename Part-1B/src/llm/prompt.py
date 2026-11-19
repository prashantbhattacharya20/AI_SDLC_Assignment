"""Versioned prompt template rendering and structured JSON instructions.

Cites: Part-1B/specs/001-code-review-assistant/plan.md (Layer 4: LLM Client Layer)
"""

from pathlib import Path

DEFAULT_PROMPT_VERSION = "v1.0.0"
SUPPORTED_PROMPT_VERSIONS = {"v1.0.0", "v2.0.0", "v2.1.0"}

VERSION_FILE_MAP = {
    "v1.0.0": "review_system_prompt_v1.txt",
    "v2.0.0": "review_system_prompt_v2.txt",
    "v2.1.0": "review_system_prompt_v2_1.txt",
}

PROMPTS_DIR = Path(__file__).resolve().parent.parent.parent / "prompts"


def get_prompt_template(version: str = DEFAULT_PROMPT_VERSION) -> str:
    """Retrieve raw prompt template by version string."""
    if version not in SUPPORTED_PROMPT_VERSIONS:
        raise ValueError(f"Unsupported prompt version '{version}'. Supported: {sorted(SUPPORTED_PROMPT_VERSIONS)}")

    # Try loading from prompts directory, fallback to embedded string if missing
    filename = VERSION_FILE_MAP.get(version, f"review_system_prompt_{version.split('.')[0]}.txt")
    prompt_file = PROMPTS_DIR / filename
    if prompt_file.exists():
        return prompt_file.read_text(encoding="utf-8")

    return (
        "You are an automated, highly precise static code analysis system.\n"
        "Analyze the provided Python source code for genuine defects across four categories:\n"
        "- BUG: Logic defects, uncaught exceptions, off-by-one errors.\n"
        "- SECURITY: Injection risks, credential leaks, insecure libraries.\n"
        "- PERFORMANCE: Algorithmic inefficiencies, redundant operations.\n"
        "- MAINTAINABILITY: Excessive complexity, cognitive debt, smells.\n\n"
        "Respond STRICTLY in JSON with a root 'findings' array matching the required schema.\n"
        "Categories: BUG, SECURITY, PERFORMANCE, MAINTAINABILITY.\n"
        "Severities: CRITICAL, HIGH, MEDIUM, LOW, INFO.\n"
    )


def render_prompt(
    code: str,
    file_path: str | None = None,
    version: str = DEFAULT_PROMPT_VERSION,
) -> str:
    """Render full LLM prompt combining instructions, metadata, and delimited source code."""
    instructions = get_prompt_template(version)

    file_header = f"File: {file_path}\n" if file_path else ""

    code_block = f"{file_header}Source Code to Review:\n```python\n{code}\n```\n"

    return f"{instructions}\n\n{code_block}\nOutput ONLY the JSON object with the 'findings' array:"
