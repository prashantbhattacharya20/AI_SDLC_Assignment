"""Unit tests for prompt template rendering and schema instructions (T008)."""

import pytest


def test_render_prompt_default_version():
    from src.llm.prompt import DEFAULT_PROMPT_VERSION, render_prompt

    code = "def hello():\n    return 'world'\n"
    rendered = render_prompt(code=code, file_path="hello.py")

    assert DEFAULT_PROMPT_VERSION == "v1.0.0"
    assert "def hello():" in rendered
    assert "hello.py" in rendered
    assert "JSON" in rendered
    assert "findings" in rendered
    assert "BUG" in rendered
    assert "SECURITY" in rendered
    assert "PERFORMANCE" in rendered
    assert "MAINTAINABILITY" in rendered


def test_render_prompt_without_file_path():
    from src.llm.prompt import render_prompt

    code = "x = 1 + 2\n"
    rendered = render_prompt(code=code)

    assert "x = 1 + 2" in rendered
    assert "JSON" in rendered


def test_prompt_version_selection():
    from src.llm.prompt import render_prompt

    code = "print('test')"
    v1_rendered = render_prompt(code=code, version="v1.0.0")
    assert "v1.0.0" in v1_rendered or "findings" in v1_rendered

    v2_1_rendered = render_prompt(code=code, version="v2.1.0")
    assert "Passive Untrusted Code Rule" in v2_1_rendered

    with pytest.raises(ValueError):
        render_prompt(code=code, version="v99.0.0")
