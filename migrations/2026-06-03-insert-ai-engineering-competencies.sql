-- Migration: insert the 4 AI-engineering competencies
--
-- The first 4 task-surfaces of the AI-Engineering task category
-- (docs/plans/2026-05-27-ai-engineering-task-category.html §"Compe-
-- tencies (topic-style)"). All ADVANCED, all with a `scope` field
-- naming the primary framework (the load-bearing signal the
-- classifier's leanest-superset rule reads).
--
-- Per the doc: 4 core competencies ship in v1. Multi-Modal and AI
-- Evaluation are carried as tasks under Production Agent Engineering
-- for now (a v1.1 follow-up adds them as their own competencies).
--
-- Apply order:
--   1. 2026-06-03-insert-python-base.sql
--   2. 2026-06-03-insert-python-ai-agent.sql
--   3. THIS FILE
--   4. 2026-06-03-bump-registry-version.sql
--
-- Deterministic UUIDs so the migration is idempotent and the same
-- competency_id can be referenced from data/generated/input_files/
-- JSON sets.

INSERT INTO competencies (competency_id, organization_id, name, proficiency, scope, created_at) VALUES
-- #1 — Production Agent Engineering
(
    'a1a1a1a1-1111-4111-8111-aaaaaaaaaaaa',
    '22222222-2222-4222-8222-222222222222',
    'Production Agent Engineering',
    'ADVANCED',
    'An engineer with ADVANCED proficiency in Production Agent Engineering designs, builds, ships, and OPERATES LLM-powered agents that are reliable in production. Primary framework: LangGraph + LiteLLM (Anthropic primary, OpenAI fallback). Scope includes: tool-use agents and the tool-calling loop (OpenAI / Anthropic function calling); structured error handling and failure surfacing instead of masking; observability and tracing of agent steps (Langfuse / OpenInference); retry, timeout, and call-budget controls; cost ceilings enforced PRE-LLM-call (not via try/except); bounded agent loops; deterministic testing of agents (mock-LLM fixtures + recorded prompts); and debugging a misbehaving agent. Familiar with langgraph, pydantic-ai, crewai, mem0, langfuse. The engineer has actually debugged a runaway agent at 3am and argued about a context budget.',
    NOW()
),
-- #2 — Multi-Agent Systems
(
    'a2a2a2a2-2222-4222-8222-aaaaaaaaaaaa',
    '22222222-2222-4222-8222-222222222222',
    'Multi-Agent Systems',
    'ADVANCED',
    'An engineer with ADVANCED proficiency in Multi-Agent Systems designs, builds, and operates systems where multiple agents coordinate to solve a problem. Primary framework: CrewAI (alt: LangGraph). Scope includes: orchestration patterns (planner/executor, supervisor/router, handoffs, fan-out/fan-in); multi-step pipelines; coordination failure modes unique to multi-agent systems (state divergence, message drift, deadlock); a deterministic tiebreaker that is NOT just another LLM call; intent routing with a confidence-escape-hatch; handoff/state threading; cost / latency budgeting across the crew; and a framework-light supervisor that can route to a general fallback when intent is ambiguous. The engineer has argued about the trade-off between determinism and capability in a production crew.',
    NOW()
),
-- #3 — Context Engineering
(
    'a3a3a3a3-3333-4333-8333-aaaaaaaaaaaa',
    '22222222-2222-4222-8222-222222222222',
    'Context Engineering',
    'ADVANCED',
    'An engineer with ADVANCED proficiency in Context Engineering designs, builds, and operates the context-windowing layer of an LLM application — the piece between the user and the model that decides what goes into the prompt. Framework-light: LiteLLM + tiktoken + Mem0 + fastembed. Scope includes: token budgets and prompt-size discipline; context-window management (pruning, summarization, retrieval-augmented context); KV-cache reuse; cost ceilings enforced at the prompt-assembly layer; long-term memory (relevance-keyed retrieval, dedup, staleness); structured-output parsers and validation at the boundary; and a self-check that surfaces p95 prompt size, cache hit rate, and quality on a held-out set. The engineer has trimmed a context budget and argued about chunking strategy.',
    NOW()
),
-- #4 — Tool Use for Agents
(
    'a4a4a4a4-4444-4444-8444-aaaaaaaaaaaa',
    '22222222-2222-4222-8222-222222222222',
    'Tool Use for Agents',
    'ADVANCED',
    'An engineer with ADVANCED proficiency in Tool Use for Agents designs, builds, and hardens the tool-calling surface of an LLM agent. Primary framework: Anthropic tool use (via LiteLLM) — also OpenAI function calling. Scope includes: tool schemas (JSON-Schema with required fields, enums, types); argument validation at the boundary (rejected BEFORE dispatch); RAG routing over a large tool catalogue (return only the relevant tools per query); tool-call repair loops (feed the structured error back to the model, cap retries, fail gracefully); distinguishing recoverable vs. terminal tool errors; and observability of tool calls (which tool, with what args, how often wrong). The engineer has shipped a tool catalogue where wrong-tool rate was a real metric on a dashboard.',
    NOW()
)
ON CONFLICT (competency_id) DO UPDATE
SET
    name = EXCLUDED.name,
    proficiency = EXCLUDED.proficiency,
    scope = EXCLUDED.scope,
    organization_id = EXCLUDED.organization_id;

-- Note: the doc lists Multi-Modal Agent Engineering and AI Evaluation
-- as candidates for v1.1. We carry them as example tasks under
-- Production Agent Engineering for now (see
-- docs/plans/2026-05-27-ai-engineering-task-category.html §"Five
-- more task examples" #3 and #7). Adding them as their own
-- competencies requires a Gemini-vision primary framework and a
-- scope text that disambiguates from the four above — addressed in
-- a follow-up migration once v1 is verified.
