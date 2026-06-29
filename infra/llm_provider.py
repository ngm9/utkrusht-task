"""LLM provider switch — Anthropic (Claude via Portkey) vs GLM (via OpenRouter).

The pipeline historically routed every "thinking" call to Claude through the
Portkey gateway. This module is the ONE place that decides whether those
Claude-role calls go to **Anthropic** or to **GLM** (Z.ai) via **OpenRouter**,
selected at runtime by the ``LLM_PROVIDER`` env var (default ``anthropic``).

``run_pipeline.py --llm-provider`` (which the trace_ui launcher passes through)
sets ``LLM_PROVIDER`` so every stage subprocess inherits it. The deliberately
OpenAI steps — answer-code (``gpt-5.x``) and the eval judge (``gpt-5.4-nano``) —
are NOT routed here; they always use OpenAI.

OpenRouter is OpenAI-API-compatible, so a GLM client is a drop-in
``openai.OpenAI`` pointed at ``https://openrouter.ai/api/v1`` — every existing
``chat.completions.create(...)`` call site works unchanged. Both clients are
wrapped by :func:`infra.tracing.client.trace_client`, so GLM calls are traced
exactly like the Anthropic ones (the trace card's model field shows which ran).

Env:
    LLM_PROVIDER         "anthropic" (default) | "glm"
    OPENROUTER_API_KEY   required when LLM_PROVIDER=glm
    OPENROUTER_GLM_MODEL GLM slug override (default "z-ai/glm-5.2")
"""
from __future__ import annotations

import os

import httpx
import openai
from portkey_ai import PORTKEY_GATEWAY_URL, createHeaders

from infra.tracing.client import trace_client

ANTHROPIC = "anthropic"
GLM = "glm"

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
# Overridable so a new GLM release is an env change, not a code change.
DEFAULT_GLM_MODEL = "z-ai/glm-5.2"

# Claude-role -> concrete Anthropic model id. The GLM side collapses every role
# onto the one flagship GLM model (one strong model, no per-role tiers).
_ANTHROPIC_MODELS = {
    "primary": "claude-opus-4-8",    # main task-generation call
    "repair": "claude-sonnet-4-6",   # cheaper retry/repair model
    "classifier": "claude-sonnet-4-6",
    "bot": "claude-sonnet-4-6",      # task_builder conversation bot
}
# DSPy/litellm model strings — the prompt-generator's COMPILE step is the only
# Claude call there (its runtime model is OpenAI and stays OpenAI).
_ANTHROPIC_DSPY = {
    "prompt_compile": "anthropic/claude-haiku-4-5",
}

# Finite timeout, mirrored from generators/task/_clients.py — a stalled upstream
# response must trip the timeout instead of wedging the whole pipeline.
_LLM_TIMEOUT = httpx.Timeout(
    connect=15.0,
    read=float(os.getenv("LLM_HTTP_READ_TIMEOUT", "600")),
    write=60.0,
    pool=15.0,
)


def active_provider() -> str:
    """The selected provider: ``"glm"`` when ``LLM_PROVIDER`` is glm/openrouter/
    z-ai, else ``"anthropic"`` (the default)."""
    p = (os.getenv("LLM_PROVIDER") or ANTHROPIC).strip().lower()
    return GLM if p in (GLM, "openrouter", "z-ai", "zai") else ANTHROPIC


def glm_model() -> str:
    """The GLM model slug sent to OpenRouter (``OPENROUTER_GLM_MODEL`` override)."""
    return (os.getenv("OPENROUTER_GLM_MODEL") or "").strip() or DEFAULT_GLM_MODEL


def resolve_model(role: str, *, provider: str | None = None) -> str:
    """Concrete chat-model id for a Claude *role* under the active provider.

    Roles: ``primary`` | ``repair`` | ``classifier`` | ``bot``. Unknown roles
    fall back to ``primary`` rather than raising — a model lookup must never
    crash a generation call site.
    """
    provider = provider or active_provider()
    if provider == GLM:
        return glm_model()
    return _ANTHROPIC_MODELS.get(role, _ANTHROPIC_MODELS["primary"])


def resolve_dspy_model(role: str, *, provider: str | None = None) -> str:
    """litellm-format model string for a DSPy Claude role (prefix-aware).

    ``configure_dspy`` routes any ``openrouter/...`` model straight to OpenRouter,
    so GLM is returned with that prefix.
    """
    provider = provider or active_provider()
    if provider == GLM:
        return f"openrouter/{glm_model()}"
    return _ANTHROPIC_DSPY.get(role, _ANTHROPIC_DSPY["prompt_compile"])


def _anthropic_client() -> openai.OpenAI:
    """Portkey gateway → Anthropic (the historical default client)."""
    return trace_client(
        openai.OpenAI(
            api_key=os.getenv("ANTHROPIC_API_KEY"),
            base_url=PORTKEY_GATEWAY_URL,
            default_headers=createHeaders(
                provider="anthropic",
                api_key=os.environ.get("PORTKEY_API_KEY"),
            ),
            timeout=_LLM_TIMEOUT,
        ),
        provider="anthropic",
    )


def _glm_client() -> openai.OpenAI:
    """Direct OpenRouter client (OpenAI-compatible) for GLM."""
    return trace_client(
        openai.OpenAI(
            api_key=os.getenv("OPENROUTER_API_KEY"),
            base_url=OPENROUTER_BASE_URL,
            timeout=_LLM_TIMEOUT,
            # Optional OpenRouter attribution headers (used for their dashboards).
            default_headers={"X-Title": "Utkrushta task-gen"},
        ),
        provider="openrouter",
    )


def make_llm_client(*, provider: str | None = None) -> openai.OpenAI:
    """A traced OpenAI-SDK client for the active provider's Claude-role calls.

    Returns the Portkey→Anthropic client by default, or a direct OpenRouter
    client when GLM is selected. Call sites keep using
    ``client.chat.completions.create(...)`` unchanged.
    """
    provider = provider or active_provider()
    return _glm_client() if provider == GLM else _anthropic_client()


def provider_request_kwargs(*, provider: str | None = None) -> dict:
    """Extra ``chat.completions.create`` kwargs for the active provider's
    large-output calls (task generation).

    GLM (z-ai via OpenRouter) is a **reasoning model**: on a big-output prompt
    its reasoning channel can consume the ENTIRE ``max_tokens`` budget before any
    answer is emitted (observed: 32K output, ``finish_reason="length"``, empty
    ``content`` → the task-gen call hard-failed). The reasoning trace is discarded
    anyway, so disable it for these calls via OpenRouter's ``reasoning`` param.
    Empty dict for anthropic/OpenAI — the param is OpenRouter-specific.
    """
    provider = provider or active_provider()
    if provider == GLM:
        return {"extra_body": {"reasoning": {"enabled": False}}}
    return {}
