"""Tests for the Anthropic<->GLM provider switch (infra/llm_provider) and the
trace_ui launcher threading it through to run_pipeline."""
from __future__ import annotations

import json

import pytest

import infra.llm_provider as p


# ----------------------------------------------------------------------
# active_provider / model resolution
# ----------------------------------------------------------------------

def test_default_provider_is_anthropic(monkeypatch):
    monkeypatch.delenv("LLM_PROVIDER", raising=False)
    assert p.active_provider() == "anthropic"


@pytest.mark.parametrize("val", ["glm", "GLM", "openrouter", "z-ai", "zai", " glm "])
def test_glm_aliases_select_glm(monkeypatch, val):
    monkeypatch.setenv("LLM_PROVIDER", val)
    assert p.active_provider() == "glm"


@pytest.mark.parametrize("val", ["anthropic", "claude", "", "nonsense"])
def test_non_glm_values_fall_back_to_anthropic(monkeypatch, val):
    monkeypatch.setenv("LLM_PROVIDER", val)
    assert p.active_provider() == "anthropic"


def test_anthropic_role_models(monkeypatch):
    monkeypatch.delenv("LLM_PROVIDER", raising=False)
    assert p.resolve_model("primary") == "claude-opus-4-8"
    assert p.resolve_model("repair") == "claude-sonnet-4-6"
    assert p.resolve_model("classifier") == "claude-sonnet-4-6"
    assert p.resolve_model("bot") == "claude-sonnet-4-6"
    # unknown role never raises — falls back to primary
    assert p.resolve_model("does-not-exist") == "claude-opus-4-8"


def test_glm_collapses_every_role_to_one_slug(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "glm")
    monkeypatch.delenv("OPENROUTER_GLM_MODEL", raising=False)
    for role in ("primary", "repair", "classifier", "bot"):
        assert p.resolve_model(role) == "z-ai/glm-5.2"


def test_glm_model_env_override(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "glm")
    monkeypatch.setenv("OPENROUTER_GLM_MODEL", "z-ai/glm-9.9")
    assert p.glm_model() == "z-ai/glm-9.9"
    assert p.resolve_model("primary") == "z-ai/glm-9.9"


def test_blank_glm_model_override_falls_back_to_default(monkeypatch):
    monkeypatch.setenv("OPENROUTER_GLM_MODEL", "   ")
    assert p.glm_model() == p.DEFAULT_GLM_MODEL


def test_dspy_model_prefixing(monkeypatch):
    monkeypatch.delenv("LLM_PROVIDER", raising=False)
    assert p.resolve_dspy_model("prompt_compile") == "anthropic/claude-haiku-4-5"
    monkeypatch.setenv("LLM_PROVIDER", "glm")
    monkeypatch.delenv("OPENROUTER_GLM_MODEL", raising=False)
    # litellm needs the openrouter/ prefix to route to OpenRouter directly.
    assert p.resolve_dspy_model("prompt_compile") == "openrouter/z-ai/glm-5.2"


def test_explicit_provider_arg_overrides_env(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "glm")
    assert p.resolve_model("primary", provider="anthropic") == "claude-opus-4-8"


# ----------------------------------------------------------------------
# client construction (no network — just base_url wiring)
# ----------------------------------------------------------------------

def test_make_client_base_urls(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "x")
    monkeypatch.setenv("OPENROUTER_API_KEY", "y")
    monkeypatch.setenv("PORTKEY_API_KEY", "z")

    monkeypatch.setenv("LLM_PROVIDER", "anthropic")
    assert "portkey" in str(p.make_llm_client().base_url)

    monkeypatch.setenv("LLM_PROVIDER", "glm")
    assert "openrouter.ai" in str(p.make_llm_client().base_url)


def test_provider_request_kwargs(monkeypatch):
    # GLM (reasoning model) → disable reasoning so it doesn't eat the token budget
    monkeypatch.setenv("LLM_PROVIDER", "glm")
    assert p.provider_request_kwargs() == {"extra_body": {"reasoning": {"enabled": False}}}
    # anthropic / default → no extra (reasoning param is OpenRouter-specific)
    monkeypatch.setenv("LLM_PROVIDER", "anthropic")
    assert p.provider_request_kwargs() == {}
    monkeypatch.delenv("LLM_PROVIDER", raising=False)
    assert p.provider_request_kwargs() == {}
    # explicit override beats env
    monkeypatch.setenv("LLM_PROVIDER", "anthropic")
    assert "extra_body" in p.provider_request_kwargs(provider="glm")


def test_glm_priced_in_table():
    from infra.pricing import price_per_million
    # The OpenRouter slug canonicalizes to "glm-5.2" — both must resolve, and
    # NOT fall through to the unknown-model default.
    assert price_per_million("z-ai/glm-5.2") == (0.95, 3.0)
    assert price_per_million("glm-5.2") == (0.95, 3.0)


# ----------------------------------------------------------------------
# trace_ui launcher threads --llm-provider through to run_pipeline
# ----------------------------------------------------------------------

def test_api_launch_threads_llm_provider(monkeypatch):
    from trace_ui import server as srv
    from trace_ui.server import RunRequest

    captured: dict = {}
    monkeypatch.setattr(srv, "_spawn_pipeline", lambda cmd: captured.update(cmd=cmd))

    resp = srv.api_launch(RunRequest(names=["Python"], proficiency="BASIC", llm_provider="glm"))
    body = json.loads(bytes(resp.body).decode())
    assert body["llm_provider"] == "glm"
    cmd = captured["cmd"]
    assert "--llm-provider" in cmd and cmd[cmd.index("--llm-provider") + 1] == "glm"


def test_api_launch_defaults_and_sanitizes_provider(monkeypatch):
    from trace_ui import server as srv
    from trace_ui.server import RunRequest

    captured: dict = {}
    monkeypatch.setattr(srv, "_spawn_pipeline", lambda cmd: captured.update(cmd=cmd))

    # default
    srv.api_launch(RunRequest(names=["Python"], proficiency="BASIC"))
    cmd = captured["cmd"]
    assert cmd[cmd.index("--llm-provider") + 1] == "anthropic"

    # junk value is coerced to anthropic, never passed through raw
    resp = srv.api_launch(RunRequest(names=["Python"], proficiency="BASIC", llm_provider="evil"))
    assert json.loads(bytes(resp.body).decode())["llm_provider"] == "anthropic"
    cmd2 = captured["cmd"]
    assert cmd2[cmd2.index("--llm-provider") + 1] == "anthropic"
