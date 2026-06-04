"""E2B v2 template: ``utkrusht-python-ai-agent`` — the AI-engineering runtime.

The agent-framework member of the Python template family (per
``docs/plans/2026-05-27-ai-engineering-task-category.html`` §"The
sandbox: the python-ai-agent template"). Carries the ~6 agent
frameworks on top of the lean ``python-base``:

* ``langgraph``        — graph-based agent orchestration (primary for
                         Production Agent Engineering + Multi-Agent Systems)
* ``pydantic-ai``      — type-safe agent API
* ``crewai``           — multi-agent crew abstraction
* ``mem0``             — long-term memory layer
* ``langfuse``         — observability / tracing
* ``openinference-instrumentation`` — OpenTelemetry-style traces
* ``litellm``          — model router (Anthropic / OpenAI / Gemini / etc.
                         via the existing Portkey gateway; the candidate
                         brings their own API key — the gate is key-free)
* ``tiktoken``         — token counting for context-budgeting
* ``fastembed``        — already baked in ``python-base``; this template
                         re-lists it in its capability sheet so the LLM
                         classifier knows embedding routes are available

The DB client + pytest + Docker + DinD set is inherited from
``python-base`` via the shared ``base_python_template()`` helper.
The agent-framework pins (crewai/langgraph/mem0 carry heavy, opinionated
deps) are isolated here so the web/DB tasks on the leaner base are
untouched — a CVE patch in agent-land doesn't trigger a web rebuild.

Two module-level exports:

* ``template``  — the imperative :class:`AsyncTemplate` build pipeline.
* ``manifest``  — the declarative capability sheet read by the LLM
  classifier and the ``templates`` SQL table.

The manifest is the union of the base's capability sheet (composed at
authoring time) plus the agent frameworks. The stored ``templates``
row is self-contained (no ``parent_template_id`` column); the
classifier reads a fully-resolved sheet.

Build:
    cd infra/e2b/templates/python-ai-agent
    python build_dev.py     # -> utkrusht-python-ai-agent-dev
    python build_prod.py    # -> utkrusht-python-ai-agent   (once verified)
"""
from __future__ import annotations

from infra.e2b.templates._base.python_common import base_python_template

# The agent frameworks — version-pinned so a rebuild is reproducible
# AND so dependency conflicts surface at build time, not weeks later
# in eval. Heavy pins (crewai/langgraph/mem0) are isolated here per
# the doc's family split; CVE patches to these don't cascade to
# python-web tasks.
_AGENT_PIP_PACKAGES = (
    # Primary agent framework
    "langgraph==0.2.50",
    "langchain==0.3.7",
    "langchain-core==0.3.21",
    "langchain-community==0.3.7",
    # Type-safe agent API
    "pydantic-ai==0.0.18",
    # Multi-agent crew
    "crewai==0.86.0",
    # Long-term memory layer
    "mem0ai==0.1.29",
    # Observability
    "langfuse==2.53.1",
    "openinference-instrumentation-langchain==0.1.24",
    # Model router — the candidate's session brings their own key
    # (Portkey-gated); the gate is LLM-free, no key in this image.
    "litellm==1.51.0",
    # Token counting for context-budgeting tasks
    "tiktoken==0.8.0",
    # The candidate-facing SDKs (Anthropic, OpenAI). The LLM ecosystem
    # sits in this image, NOT in the base — the family split is the
    # boundary the LLM classifier's leanest-superset rule reads.
    "anthropic==0.39.0",
    "openai==1.58.1",
    "google-generativeai==0.8.3",
    # Local serving for the candidate's session (Ollama-style not
    # needed; the LLM is on the candidate's key via Portkey).
)

# The AI-agent member's capability sheet — base union + agent frameworks.
# Composed at authoring time (no query-time union), so the stored
# ``templates`` row is self-contained.
manifest = {
    "template_id": "utkrusht-python-ai-agent",
    "status": "built",
    "primary_runtime": "python",
    "personas": ["agent_engineer", "mle"],
    "eval_methods": ["test_suite"],
    "capabilities": {
        "language_versions": {"python": "3.12"},
        # Frameworks the AI-agent image alone supports. The classifier
        # reads this list to disambiguate from python-web (which lists
        # web frameworks instead).
        "frameworks": [
            # Agent frameworks (the primary)
            "langgraph",
            "pydantic-ai",
            "crewai",
            "mem0",
            # Model routing
            "litellm",
            # Observability
            "langfuse",
            "openinference-instrumentation",
            # Embedding (re-listed from base; classifier wants it here)
            "fastembed",
            # Provider SDKs (the candidate's session key routes via these)
            "anthropic",
            "openai",
            "google-generativeai",
        ],
        # DB clients inherited from the base (composed for self-containment).
        "datastores": ["postgres", "mysql", "mongo", "redis", "qdrant"],
        "protocols": ["rest", "websocket"],
        # Tools — base set + agent-specific.
        "tools": [
            # From python-base
            "pytest",
            "pytest-asyncio",
            "docker",
            "docker-compose",
            "git",
            "jq",
            "postgresql-client",
            "default-mysql-client",
            "psycopg2-binary",
            "pymongo",
            "redis",
            "httpx",
            "requests",
            "pandas",
            "numpy",
            "ttyd",
            "code-server",
            "adminer",
            # AI-agent additions
            "litellm",
            "tiktoken",
            "fastembed",
            "langfuse",
        ],
        "requires": {"browser": False, "gpu": False},
        "tags": ["python-ai-agent", "family-member", "agent-frameworks"],
    },
    "build_cmd": "pip install --break-system-packages -r requirements.txt",
    "test_cmd": "python -m pytest -q --tb=short",
    "compile_cmd": "python -m compileall -q .",
    "install_cmd": "apt-get install -y python3 python3-pip",
    "install_verify": "python3 --version",
    "install_seconds": 15,
    "description": (
        "AI-agent Python 3.12 runtime. Layers the agent frameworks "
        "(langgraph, pydantic-ai, crewai, mem0) on the lean python-base "
        "substrate, plus LiteLLM for model routing and tiktoken for "
        "context budgeting. Provider SDKs (anthropic, openai, "
        "google-generativeai) are pre-installed so the candidate's "
        "agent code can call models directly via the candidate's own "
        "API key. Observability via langfuse + openinference. The gate "
        "is LLM-free — no API key sits in this image at generation; "
        "the candidate's session brings their own key in."
    ),
}

template = (
    base_python_template()
    .run_cmd(
        "pip install --no-cache-dir --break-system-packages "
        + " ".join(_AGENT_PIP_PACKAGES)
    )
    .copy("start.sh", "/usr/local/bin/start.sh")
    .run_cmd("chmod +x /usr/local/bin/start.sh")
    .set_workdir("/home/user")
    .set_start_cmd("sudo /usr/local/bin/start.sh", "sleep 20")
)
