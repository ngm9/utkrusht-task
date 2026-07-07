"""Deterministic strip of template-pre-installed package pins from a generated
requirements.txt — prevents the readiness gate's pip install from hitting a
version conflict with the image's baked-in LLM stack (the GLM
ResolutionImpossible failure: httpx>=0.28 + litellm>=1.55 don't co-resolve and
clash with the image's litellm==1.51 / anthropic==0.39 / openai==1.58)."""
from __future__ import annotations

from generators.task.creator import _strip_preinstalled_pins


def test_strips_llm_stack_for_python_ai_template():
    files = {"requirements.txt": (
        "fastapi==0.115.6\n"
        "litellm>=1.55,<1.60\n"
        "httpx>=0.28,<0.29\n"
        "redis==5.2.1\n"
        "openai==1.58.1\n"
        "anthropic==0.39.0\n"
        "tiktoken==0.8.0\n"
    )}
    _strip_preinstalled_pins(files, "utkrusht-python-ai")
    req = files["requirements.txt"]
    # task-specific deps kept — AND litellm is kept: the live image does not
    # actually pre-install it on the gate's interpreter, so run.sh must install
    # it (stripping it caused ModuleNotFoundError: No module named 'litellm').
    for keep in ("fastapi", "redis", "tiktoken", "litellm"):
        assert keep in req, f"{keep} should be kept"
    # genuinely pre-installed stack still stripped (image provides them)
    for drop in ("httpx", "openai", "anthropic"):
        assert drop not in req, f"{drop} should be stripped"


def test_litellm_is_not_stripped_so_runsh_installs_it():
    # Regression guard for the readiness-gate failure: the utkrusht-python-ai
    # image lacks litellm on the python run.sh uses, so it must NOT be stripped.
    files = {"requirements.txt": "litellm==1.40.10\nredis==5.2.1\n"}
    _strip_preinstalled_pins(files, "utkrusht-python-ai")
    assert "litellm" in files["requirements.txt"]


def test_noop_for_template_without_a_declared_set():
    files = {"requirements.txt": "litellm==1.55\nhttpx==0.28\n"}
    before = files["requirements.txt"]
    _strip_preinstalled_pins(files, "utkrusht-python")  # plain python: no LLM stack
    assert files["requirements.txt"] == before


def test_noop_for_none_template():
    files = {"requirements.txt": "httpx==0.28\n"}
    before = files["requirements.txt"]
    _strip_preinstalled_pins(files, None)
    assert files["requirements.txt"] == before


def test_preserves_comments_and_include_lines():
    files = {"requirements.txt": "# core deps\nfastapi==0.115\n-r base.txt\nhttpx==0.28\n"}
    _strip_preinstalled_pins(files, "utkrusht-python-ai")
    req = files["requirements.txt"]
    assert "# core deps" in req and "-r base.txt" in req and "fastapi" in req
    assert "httpx" not in req


def test_name_match_is_case_and_separator_insensitive_and_handles_extras():
    files = {"app/requirements.txt": (
        "uvicorn[standard]==0.34\n"   # kept (not pre-installed), extras stripped from name match
        "LangChain_Core==0.3\n"        # stripped — normalizes to langchain-core
        "OpenAI==1.58\n"               # stripped — case-insensitive
    )}
    _strip_preinstalled_pins(files, "utkrusht-python-ai")
    req = files["app/requirements.txt"]
    assert "uvicorn" in req
    assert "LangChain_Core" not in req
    assert "OpenAI" not in req


def test_noop_when_no_requirements_file():
    files = {"run.sh": "echo hi"}
    _strip_preinstalled_pins(files, "utkrusht-python-ai")
    assert files == {"run.sh": "echo hi"}


def test_does_not_mutate_when_nothing_to_strip():
    files = {"requirements.txt": "fastapi==0.115\nredis==5.2\n"}
    before = files["requirements.txt"]
    _strip_preinstalled_pins(files, "utkrusht-python-ai")
    assert files["requirements.txt"] == before  # untouched, trailing newline intact
