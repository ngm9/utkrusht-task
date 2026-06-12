"""Shared LLM + Portkey clients for the task-generation package.

One init point so ``evaluator``, ``creator`` (later), and ``multiagent.py``
import the same client instances instead of each spinning up their own.

Two clients today:

* ``openai_client`` — Anthropic (Claude) routed via the Portkey gateway. The
  default LLM for the eval critics and the main task-generation call.
* ``openai_via_portkey`` — OpenAI (GPT) routed via Portkey. Used for the
  answer-code step where structured-output support is stronger.

Lifted from the module-level globals of ``multiagent.py`` unchanged.
"""
from __future__ import annotations

import os

import httpx
import openai
from portkey_ai import PORTKEY_GATEWAY_URL, createHeaders

from infra.tracing.client import trace_client


# A FINITE timeout on the LLM HTTP clients. Previously these used
# ``httpx.Timeout(None)`` (infinite) — a single stalled upstream response (e.g.
# Portkey/provider hiccup mid-generation) would then hang the whole task-
# generation pipeline indefinitely with no recovery (observed: the solution-code
# step wedged 40+ minutes on a half-delivered response). ``read`` is generous so
# legitimately long reasoning-model generations aren't cut off, but a true hang
# now trips the timeout and the OpenAI SDK's built-in retries kick in.
_LLM_TIMEOUT = httpx.Timeout(
    connect=15.0,
    read=float(os.getenv("LLM_HTTP_READ_TIMEOUT", "600")),
    write=60.0,
    pool=15.0,
)


# Anthropic (Claude) via Portkey — the default LLM client.
_ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

openai_client = trace_client(
    openai.OpenAI(
        api_key=_ANTHROPIC_API_KEY,
        base_url=PORTKEY_GATEWAY_URL,
        default_headers=createHeaders(
            provider="anthropic",
            api_key=os.environ.get("PORTKEY_API_KEY"),
        ),
        timeout=_LLM_TIMEOUT,
    ),
    provider="anthropic",
)

# Eval-critic model — Claude Sonnet 4.6 via Portkey.
EVAL_MODEL = "claude-sonnet-4-6"


# Portkey → OpenAI client for the answer-code step. Uses GPT-5.4 (cheaper +
# stronger structured-output support than Claude for this specific call) but
# routed via Portkey for unified observability/billing.
openai_via_portkey = trace_client(
    openai.OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=PORTKEY_GATEWAY_URL,
        default_headers=createHeaders(
            provider="openai",
            api_key=os.environ.get("PORTKEY_API_KEY"),
        ),
        timeout=_LLM_TIMEOUT,
    ),
    provider="openai",
)

ANSWER_CODE_MODEL = os.getenv("ANSWER_CODE_MODEL", "gpt-5.4")
