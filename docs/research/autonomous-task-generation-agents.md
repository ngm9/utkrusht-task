# Autonomous Task Generation: Research & Architecture

> **Status**: Research complete. Phase 1 POC next.
> **Date**: March 2026

---

## 1. Why We're Building This

### The Problem We Solve

Organizations come to us with messy, varied inputs:

- "We need to hire 3 senior Go engineers for our payments team"
- A job description PDF with a tech stack buried in bullet points
- "Our last batch of tasks were too easy — candidates finished in 10 minutes"
- "We want debugging tasks that test production thinking, not just coding"
- A Slack message: "Can you make something for our ML team? They mostly do RAG pipelines."

Our job is to take these messy inputs and produce **high-quality, deployable technical assessments** that reflect our taste and standards. The inputs vary wildly. The output must be consistently excellent.

### What Makes Utkrushta Different

We are not HackerRank. We are not CodeSignal. Our assessments are fundamentally different:

- **Full AI access.** Candidates use AI assistants naturally, exactly like real work. We don't fight AI — we design around it. The signal comes from judgment and decision-making, not memorization or typing speed.
- **Real infrastructure.** We deploy databases, K8s clusters, running APIs. Candidates work in real engineering environments, not sandboxed editors.
- **Our taste is the product.** Anyone can generate a coding challenge with GPT. What makes our tasks valuable is the domain knowledge, the realistic scenarios, the calibrated difficulty, the deployability. That taste is encoded in our guidelines, our prompts, and our verification standards.

### Why Automate

Today, task generation is manual: a human runs CLI commands, selects prompt files, reviews output, publishes. This works at 5-10 tasks per week. It doesn't work at 100 tasks per day, across 15+ tech stacks, 6 task types, and multiple customer domains.

We need an autonomous system that:
1. Understands varied customer inputs
2. Applies our domain knowledge and taste consistently
3. Generates diverse, high-quality, deployable tasks
4. Verifies its own work against reality (not just LLM-checking-LLM)
5. Scales without proportional human effort

---

## 2. Requirements

### Varied Customer Domains

A fintech company wants CSV batch processing tasks for their Java team. An AI startup wants RAG pipeline debugging. A DevOps consultancy wants K8s misconfiguration tasks. Each domain brings:

- Industry-specific scenarios (financial transactions, healthcare data, e-commerce carts)
- Tech stack preferences (and strong opinions about them)
- Compliance considerations (PCI for fintech, HIPAA for healthcare)
- Organizational culture ("we value clean architecture" vs "we value shipping speed")

The generation system must incorporate domain context without requiring domain-specific prompt files for every combination. The combinatorial space (task type × tech stack × proficiency × domain) is too large for static prompts.

### Six Task Types

We define six categories of work, each testing a different kind of engineering judgment:

**BUILD** — Extend a given repo or build from a skeleton. Tests architectural judgment: where and how to add a feature. *Example: "Extend this FastAPI service with a CSV batch processing endpoint for financial transactions."*

**DEBUG** — Given a broken service, find and fix what's wrong. Tests hypothesis formation and systematic investigation. *Example: "This Kafka consumer is losing messages under load. Tests are failing. Diagnose and fix."*

**DESIGN REVIEW** — Review a technical design document. Tests systems thinking and trade-off analysis. *Example: "Review this payment service design doc. What failure modes are missing?"*

**PR REVIEW** — Review a pull request, find issues, suggest improvements. Tests pattern recognition and communication. *Example: "Review this PR that adds transaction rollback logic."*

**UX / CRITICAL THINKING** — Given a design mockup and product scenario, critique or implement. Tests product thinking and user empathy. *Example: "This fintech dashboard's filter UX has a 60% drop-off. What's wrong?"*

**MANAGE INFRA** — Fix misconfigurations, diagnose deployment issues. Tests infrastructure and operational knowledge. *Example: "This K8s deployment has misconfigured ingress gateways. Traffic isn't routing."*

Each task type has a different generation pattern (single-phase vs two-phase), different artifacts (code, configs, design docs, logs, error output), and different verification needs.

### Opinionated by Design

Technical work is opinionated. A "good" Java task at one organization is different from a "good" Java task at another. Our system must:

- Apply Utkrushta's base standards (what makes any task good)
- Layer customer-specific preferences on top (their tech stack opinions, difficulty calibration, domain context)
- Maintain consistency across tasks (a "BASIC" task should feel BASIC regardless of tech stack)
- Adapt to emerging skill areas (agentic development, context engineering, RAG pipelines) without waiting for hand-crafted prompts

### Intelligent Verification

Generated tasks must pass verification before publishing:

- **Structural**: Required files present, code parses, schemas valid, README has required sections
- **Deployability**: Docker configs build, services start, health checks pass, ports are correct
- **Test correctness**: For DEBUG tasks — tests fail on the buggy version, pass on the correct version
- **Answer validity**: The answer code actually solves the described problem
- **Deduplication**: Not too similar to existing tasks (embedding similarity check)
- **Difficulty calibration**: Appropriate for the stated proficiency level
- **Domain relevance**: The scenario is realistic for the specified industry/domain

The system should self-correct: if verification reveals issues, fix them and re-verify — not just flag and fail.

---

## 3. What We Learned: Mental Frameworks

### It's Not a Pipeline

The initial instinct was to treat task generation as a fixed pipeline: inputs → scenarios → generate → eval → publish. This is how the current CLI works.

This framing is wrong. Task generation is a **dynamic graph** where the path depends on:
- What task type was requested (BUILD follows a different path than DEBUG)
- What domain context exists (a fintech customer's tasks need different scenarios than a SaaS company's)
- What the verification tools reveal (a Docker config that doesn't build changes the generation path)
- Whether the human provided clear requirements or something ambiguous that needs clarification

The right mental model is three layers:

```
                    ┌─────────────────────────┐
                    │      INTAKE AGENT        │
                    │   (understand intent)    │
                    └────────────┬────────────┘
                                 │
                    Structured understanding:
                    - What competencies?
                    - What task type(s)?
                    - What constraints?
                    - What customer context?
                                 │
                    ┌────────────▼────────────┐
                    │    GENERATION GRAPH      │
                    │   (path depends on       │
                    │    intake output)        │
                    │                          │
                    │   ┌──► BUILD             │
                    │   ├──► DEBUG             │
                    │   ├──► PR REVIEW         │──► different prompts,
                    │   ├──► DESIGN REVIEW     │   different tools,
                    │   ├──► MANAGE INFRA      │   different eval criteria
                    │   ├──► UX / CRITICAL     │
                    │   └──► hybrid / custom   │
                    │                          │
                    └────────────┬────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │   VERIFICATION TOOLS     │
                    │   (ground truth, not     │
                    │    LLM guessing)         │
                    │                          │
                    │   parse_code()           │
                    │   validate_dockerfile()  │
                    │   run_tests()            │
                    │   check_deployability()  │
                    └────────────┬────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │    EVAL + PUBLISH        │
                    └─────────────────────────┘
```

**Layer 1: Intake** — Convert varied, messy inputs into a structured task request. This needs LLM reasoning (understanding a job description, inferring proficiency levels, retrieving customer context).

**Layer 2: Generation** — Navigate a branching graph of generation strategies based on the task request. Different task types use different prompts, different tools, different numbers of generation phases. The generation agent has access to our domain knowledge (guidelines, prompt libraries) and verification tools.

**Layer 3: Verification** — Check work against reality using deterministic tools (parse code, build Docker, run tests, deploy to sandbox). These tools give the agent ground truth signals that LLMs can't fabricate.

### The Prompt Question

We have 80+ hand-crafted prompt files encoding deep domain knowledge about what makes good tasks for specific tech stacks at specific proficiency levels. This is real value.

But static prompts don't scale to the combinatorial space of 6 task types × 15+ tech stacks × 3+ proficiency levels × N customer domains. There's no prompt file for "Go + Kafka + DEBUG + INTERMEDIATE + fintech where the candidate demonstrates systematic investigation."

The resolution: **prompts become domain knowledge that the agent loads as context, not fixed scripts it follows.** The agent's behavior (how to generate, when to use tools, how to verify) is defined once. The domain knowledge (what makes a good Java BASIC task, what fintech scenarios look like) is loaded per request from our knowledge base.

This means our job shifts from writing complete prompts to **curating domain knowledge**: guidelines per task type, per tech stack, per proficiency level. The agent assembles the right knowledge for each request. New combinations work without new prompt files — the agent composes from existing guidelines.

Our existing prompts are the starting point for this knowledge base. They don't get thrown away — they get decomposed into reusable pieces.

### Generate Tasks Directly, Not Prompts

We considered a two-step approach: an LLM generates a prompt, then that prompt generates a task. We decided against it.

The intermediate prompt is a leaky abstraction. The generating LLM already has access to the same context — why add indirection? Task generation is an offline activity (no user is waiting), tasks are generated once and deployed many times, and we can always iterate on a bad task. The inspectability benefit of an intermediate prompt doesn't justify the added complexity and failure modes.

Instead: the agent receives all context (guidelines, competency scope, org preferences, scenario) and generates the task directly. The "prompt construction" is the agent assembling the right context — not a separate generation step.

### Tools Are the Differentiator

The biggest quality improvement comes not from better LLM prompting but from **verification tools that give the agent ground truth**.

An agent that generates a task and checks it with another LLM is LLM-checking-LLM — correlated blind spots. An agent that generates a task and then runs `docker compose up` to verify it actually deploys gets real signal. An agent that runs the answer code against the test suite knows for certain whether the answer is correct.

The self-correcting loop — generate → verify with tools → fix issues → re-verify — is where the Anthropic Agent SDK's sub-agent pattern and context management become valuable:

```
┌─ Generator Sub-Agent (isolated context) ──────────────────────┐
│                                                                │
│  LLM: "I'll generate a Kafka consumer debugging task..."      │
│       → generates code files                                   │
│                                                                │
│  Tool: verify_code("java", Main.java)                         │
│       → "CompileError: missing import on line 23"              │
│                                                                │
│  LLM: "Let me fix that import..."                             │
│       → fixes code                                             │
│                                                                │
│  Tool: run_tests(answer_code, test_files)                     │
│       → "2/3 pass. testRebalancing fails: AssertionError"     │
│                                                                │
│  LLM: "The rebalancing test fails because I didn't handle     │
│        consumer group reassignment. Let me fix..."             │
│       → fixes answer code                                      │
│                                                                │
│  Tool: run_tests(answer_code, test_files)                     │
│       → "3/3 pass"                                             │
│                                                                │
│  LLM: "Task verified and complete."                           │
│       → returns final TaskOutput                               │
│                                                                │
│  (6 turns, ~15K tokens. Context managed automatically.)       │
└───────────────────────────────────────────────────────────────┘
         │
         │ Parent receives: just the TaskOutput
         │ (not the 15K tokens of conversation)
         ▼
```

The loop can run for many turns. The SDK manages the growing context automatically. The parent agent only sees the final, verified result.

### Framework Choice: Leave the Door Open

We evaluated LangGraph, DSPy, CrewAI, AutoGen, OpenAI Agents SDK, Anthropic Agent SDK, Pydantic AI, and raw tool-use API.

**What we ruled out:**
- **CrewAI / AutoGen**: Role-playing and actor-based patterns don't fit our problem. We have a structured generation process, not agents debating.
- **LangGraph**: Powerful graph framework with checkpointing and human-in-the-loop built in. But our immediate need (Scenario A: self-correction within a single generation run) doesn't require graph-level infrastructure. The state machine is simple enough for Supabase + code. Revisit if graph complexity grows with 5+ task types.

**What remains viable:**
- **Anthropic Agent SDK**: Best built-in support for the generate → verify → improve loop. Automatic context management. Sub-agent isolation. But locked to Claude models.
- **Pydantic AI + Portkey**: Model-agnostic (swap GPT ↔ Claude by changing a string). Type-safe structured outputs. Officially supports Portkey. But no automatic context management — you build it (feasible, ~20-50 lines for our use case).
- **Raw tool-use API + Portkey**: Maximum control, zero dependencies. Same capabilities as Pydantic AI but more boilerplate.

**The trade-off is model flexibility vs built-in context management.** The Anthropic SDK gives you sub-agents and automatic context compaction for free, but locks you to Claude. Pydantic AI (or raw API) keeps you model-agnostic but you manage context yourself.

**For Phase 1, we're leaving this choice open.** The architecture — short-lived focused agents, your code as orchestrator, tools for verification, Supabase for state — works with any of these options. The tools are Python functions (portable). The domain knowledge is in files (portable). The structured output schemas are Pydantic models (portable). We can start with either approach and switch without rewriting the valuable parts.

### DSPy: Later, When We Have Data

DSPy is a prompt optimization framework, not an agent framework. It finds the optimal prompting strategy (instructions, few-shot examples, chain-of-thought decomposition) by optimizing against a quality metric on a dataset.

This is directly relevant to our prompt question — instead of hand-tuning 80+ prompts, define signatures and let DSPy optimize. But it requires a gold-standard dataset of human-rated tasks (50+ per task type). We don't have this yet.

**Action: Start collecting rated tasks now.** Every task a human reviews and rates is a data point for future DSPy optimization. Build the dataset passively while running Phase 1.

### Model Selection: Let Data Decide

We currently use GPT-5.2 for task generation and Claude Opus 4.6 for development. Both are strong. Rather than picking one on gut feel:

- **Run a blind comparison**: 30 tasks generated by each model, same inputs, domain expert rates blind
- **If one wins >65% of comparisons**, it's meaningfully better for this specific use case
- **If tied (45-55%)**, use the cheaper one — or use both (GPT for generation, Claude for eval) to get diversity of error detection
- **Cross-provider evaluation**: Different models have different blind spots. Using GPT to generate and Claude to evaluate (or vice versa) catches more errors than same-model self-evaluation

The system should be designed so any step can use any model. Portkey makes provider switching trivial. Track quality metrics per model per step. Re-evaluate on every major model release.

---

## 4. Phase 1: POC

### Goal

Achieve parity with the current CLI-driven task generation, but with:
1. Agentic self-correction (generate → verify → fix loop)
2. State tracking in Supabase
3. At least one verification tool integrated
4. Architecture that supports future task types and customer context

### What Parity Means

The current system (`multiagent.py`) generates BUILD (code extension) tasks. Phase 1 generates the same kind of tasks, same quality, but with:
- The generation agent using verification tools to self-correct
- Run state persisted in Supabase (`task_generation_runs` table)
- Domain knowledge loaded from existing prompt files (not rewriting them)
- A second task type (DESIGN REVIEW — simplest to add) to prove the architecture handles multiple types

### Architecture

```
┌──────────────────────────────────────────────────────────────┐
│  ORCHESTRATOR (your Python code — deterministic)              │
│                                                               │
│  1. Parse inputs, load context                                │
│  2. Load domain knowledge (prompt files / guidelines)         │
│  3. Fetch competency scope from Supabase                      │
│  4. Update run state → "generating"                           │
│     │                                                         │
│     ▼                                                         │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  GENERATOR AGENT (LLM + tools, isolated context)       │  │
│  │                                                         │  │
│  │  Receives: guidelines + competency + requirements       │  │
│  │  Tools: verify_code, check_file_structure,              │  │
│  │         validate_dockerfile, run_tests                  │  │
│  │                                                         │  │
│  │  Generates task → verifies → fixes → re-verifies       │  │
│  │  Returns: verified TaskOutput                           │  │
│  └────────────────────────────┬───────────────────────────┘  │
│     │                                                         │
│     ▼                                                         │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  EVAL AGENT (LLM, fresh isolated context)              │  │
│  │                                                         │  │
│  │  Receives: TaskOutput + eval rubric (NOT generation     │  │
│  │           history — can't be biased by it)              │  │
│  │  Returns: score + feedback                              │  │
│  └────────────────────────────┬───────────────────────────┘  │
│     │                                                         │
│     ├── score >= threshold ──► Publish (GitHub + Supabase)    │
│     │                         Update run state → "published"  │
│     │                                                         │
│     └── score < threshold ──► Retry from generator with       │
│                               eval feedback (max 2 retries)   │
│                               Update run state → "retrying"   │
│                                                               │
│     If max retries exceeded → Update run state → "failed"     │
└──────────────────────────────────────────────────────────────┘
```

### Framework Decision for Phase 1

**Option A: Anthropic Agent SDK** — Use Claude Opus 4.6 for the generator and eval agents. Get sub-agent isolation and context management for free. Evaluate task quality against current GPT-5.2 baseline.

**Option B: Pydantic AI + Portkey** — Use GPT-5.2 (current known-good model) for generation. Build the agent loop with Pydantic AI's `@agent.tool` and `result_type`. Manage context manually (short-lived agents, unlikely to need trimming in Phase 1).

**Option C: Raw API + Portkey** — Same as Option B but without Pydantic AI. More boilerplate, fewer dependencies.

**We'll decide after running the model comparison.** If Claude Opus generates tasks as well as GPT-5.2, Option A is cleanest. If GPT-5.2 is meaningfully better, Option B or C preserves model flexibility.

**Regardless of choice:** tools are Python functions, domain knowledge is in files, schemas are Pydantic models. All portable between options.

### Immediate Next Steps

1. **Model comparison**: Generate 30 tasks with Claude Opus 4.6, compare blind against 30 from GPT-5.2
2. **First verification tool**: Build `verify_code(language, code)` — syntax checking for Python, Java, Go, JS
3. **Supabase table**: Create `task_generation_runs` for state tracking
4. **Domain knowledge extraction**: Take 3-5 existing prompt files and decompose them into structured guidelines (test whether the agent generates equivalent quality from guidelines vs the monolithic prompt)
5. **DESIGN REVIEW prototype**: Generate one design review task to prove the architecture handles a second task type
6. **Start rating dataset**: Every task reviewed by a human gets a 1-5 rating stored. Build toward the 50-task DSPy threshold.

---

## Appendix: Framework Comparison Summary

| | Anthropic Agent SDK | Pydantic AI + Portkey | Raw API + Portkey |
|---|---|---|---|
| **Model flexibility** | Claude only | Any model | Any model |
| **Context management** | Automatic compaction + sub-agents | Manual (history_processors) | Manual |
| **Tool ergonomics** | `@tool` decorator | `@agent.tool` + Pydantic types | Manual JSON schemas |
| **Structured output** | Tool use | Pydantic `result_type` | Manual validation |
| **Self-correcting loop** | Built-in agent loop | Built-in agent loop | ~15 lines of code |
| **Dependencies** | claude-agent-sdk | pydantic-ai | Just API client |
| **Migration cost if wrong** | Rewrite agent loop (~50 lines), keep tools + knowledge + schemas | Same | Same |

---

## 5. What We Don't Know Yet: Experiments on the Road to Production

Phase 1 is a POC. Getting from POC to the production system that generates 100 tasks/day requires answers to questions we can only learn by building.

### Model Quality for Task Generation

**Experiment**: Blind comparison — 30 tasks from GPT-5.2, 30 from Claude Opus 4.6, same inputs.

**What we'll learn**: Which model produces better assessment tasks. This isn't about general benchmarks — it's about OUR specific task quality criteria (realistic scenarios, appropriate difficulty, deployable code, good answer keys). The winner determines our framework choice.

**What we might discover**: They could be tied. Or one could be clearly better for code-heavy tasks (BUILD, DEBUG) while the other is better for reasoning-heavy tasks (DESIGN REVIEW). If so, a multi-model strategy makes sense — and that rules out the Anthropic SDK as the sole framework.

### Guidelines vs Monolithic Prompts

**Experiment**: Take 3 existing prompt files (e.g., Java BASIC, Python INTERMEDIATE, Go BASIC). Decompose each into structured guidelines. Generate 10 tasks with the original monolithic prompt, 10 with the decomposed guidelines fed to an agent. Blind quality comparison.

**What we'll learn**: Can the agent compose tasks from guidelines as well as from hand-crafted prompts? If yes, we can scale to new combinations without writing prompt files. If no, we need to understand what the monolithic prompts capture that guidelines miss — and whether that gap is fixable.

**What we might discover**: The monolithic prompts might encode subtle things (ordering of instructions, specific phrasing that steers the model) that are hard to decompose. Or the agent with guidelines might actually produce MORE diverse tasks because it's not locked into one prompt's framing.

### Self-Correction Loop Effectiveness

**Experiment**: Generate 50 tasks with verification tools enabled (self-correcting loop) and 50 without (current approach: generate once, eval, retry from scratch if it fails).

**What we'll learn**: Does tool-based self-correction improve first-pass quality? Reduce retries? Produce more deployable tasks? At what cost increase?

**What we might discover**: Self-correction might add cost without improving quality (the model's first attempt is usually good enough). Or it might be transformative for specific task types (MANAGE INFRA tasks might fail deployment often without self-correction). The answer determines how much we invest in verification tools.

### Context Window Pressure

**Experiment**: Run the generator agent on 20 complex tasks (multi-file, Docker, multiple verification rounds) and measure peak context usage.

**What we'll learn**: Whether context management is a real problem or a theoretical one. If peak context is 30K tokens in a 200K window, we don't need automatic compaction — and model flexibility (Pydantic AI) wins over context management (Anthropic SDK).

**What we might discover**: Some task types (MANAGE INFRA with K8s configs, DEBUG with large codebases) might push context harder than others. We might need sub-agent isolation only for specific task types, not universally.

### Deduplication at Scale

**Experiment**: Generate embeddings for all existing tasks (~200). Measure cosine similarity distributions. Determine the threshold where tasks are "too similar."

**What we'll learn**: How to set the dedup threshold. Whether embedding similarity correlates with human judgment of "these tasks are basically the same."

**What we might discover**: Simple embedding similarity might not be enough — two tasks about "REST API CRUD" might have high similarity but test completely different competencies. We might need structured dedup (same competency + same scenario pattern = duplicate) rather than pure embedding distance.

### Customer Context Injection

**Experiment**: Generate 10 tasks with no org context and 10 with rich org context (industry, preferences, past feedback) for a simulated customer profile.

**What we'll learn**: How much does org context improve task relevance? Is the improvement worth the added complexity?

**What we might discover**: Org context might matter a lot for domain-specific tasks (fintech, healthcare) and barely matter for generic ones (Python BASIC). This tells us whether to invest in rich org profiles or keep it simple.

### Task Type Transferability

**Experiment**: Build DEBUG task generation using the same agent architecture as BUILD. Measure: how much new code was needed? How much was reused?

**What we'll learn**: Whether the plugin architecture actually works — can we add a new task type by writing guidelines + a generation phase definition, or does each type need significant custom code?

**What we might discover**: The two-phase pattern (clean artifact → inject flaws) might need fundamentally different tooling than the single-phase pattern (generate incomplete code). If so, "plugin" is the wrong metaphor — it's more like "two distinct generation engines with shared infrastructure."

### Human-in-the-Loop Calibration

**Experiment**: Generate 100 tasks over 2-3 weeks. Have humans review all of them and rate 1-5. Track auto-eval scores (LLM eval) against human ratings.

**What we'll learn**: How well our LLM eval correlates with human judgment (Cohen's kappa). At what eval score threshold we can safely auto-approve without human review.

**What we might discover**: The correlation might be low (kappa < 0.5), meaning our eval rubric needs work before we can trust auto-approval. Or it might be high for some task types (DESIGN REVIEW is easier to evaluate) and low for others (BUILD tasks where "quality" is subjective). This determines the path from supervised to autonomous generation.

### Cost Economics

**Experiment**: Track end-to-end cost for 50 tasks across different task types. Break down by: intake, generation, verification tools, evaluation, retries.

**What we'll learn**: The actual cost per published task. Where the money goes. Whether the self-correction loop is cost-effective (does $0.50 of extra verification save $3 of failed-generation retries?).

**What we might discover**: Some task types are dramatically more expensive than others (MANAGE INFRA with Docker verification vs DESIGN REVIEW with just text). This informs pricing, prioritization, and where to invest in cost optimization (cheaper models, better prompts, or fewer retries).

### DSPy Optimization Readiness

**Milestone, not experiment**: When we have 50+ human-rated tasks per task type, run DSPy optimization. Compare optimized prompts against hand-crafted guidelines.

**What we'll learn**: Whether systematic prompt optimization outperforms our hand-crafted knowledge. How much quality improvement is possible through optimization alone.

**What we might discover**: DSPy might find that our guidelines are already near-optimal (diminishing returns). Or it might find a completely different prompting strategy that works better — which would reshape how we think about domain knowledge encoding.

---

### Context Engineering: Fundamentals

Context engineering is the discipline of deciding **what information goes into the LLM's context window, when, and in what form.** It's the difference between dumping everything you have into a prompt and deliberately curating what the model sees.

**Why it matters**: An LLM's output is a function of its input. Same model, same temperature, different context → different quality output. Most "prompt engineering" failures are actually context engineering failures — the model had the wrong information, or too much information, or the right information buried under noise.

**The core mental framework: Every token in context should earn its place.**

Think of context like a meeting agenda. You wouldn't invite 50 people to a meeting because "they might be relevant." You invite the people who need to be there, with a clear agenda, and the right pre-reads sent in advance. Context engineering is the same discipline applied to LLM inputs.

**The five questions for every LLM call:**

1. **What does this agent need to know to do its job?** (Not "what COULD be relevant" — what MUST it know?)
2. **What would actively hurt if included?** (Contradictory information, outdated context, irrelevant examples that steer the model wrong)
3. **What's the right level of detail?** (The agent generating a task needs competency scope details. It doesn't need the full org billing history.)
4. **What order should information appear?** (Models pay more attention to the beginning and end of context. Put critical instructions first, reference material in the middle, the specific task last.)
5. **What can be retrieved on-demand vs pre-loaded?** (Static guidelines can be pre-loaded. Customer-specific context should be fetched by a tool when the agent decides it's relevant.)

**Three categories of context for our system:**

```
┌───────────────────────────────────────────────────────────┐
│                    CONTEXT WINDOW                          │
│                                                           │
│  ┌─────────────────────────────────────────────────────┐ │
│  │  STATIC CONTEXT (loaded once, same every run)        │ │
│  │  • Agent behavioral instructions                     │ │
│  │  • Task type guidelines                              │ │
│  │  • Proficiency level definitions                     │ │
│  │  • Output schema requirements                        │ │
│  │  • Verification checklist                            │ │
│  └─────────────────────────────────────────────────────┘ │
│  ┌─────────────────────────────────────────────────────┐ │
│  │  PER-REQUEST CONTEXT (assembled before generation)   │ │
│  │  • Competency scope (from Supabase)                  │ │
│  │  • Org preferences (from Supabase, if available)     │ │
│  │  • Selected scenario                                 │ │
│  │  • User's specific requirements & constraints        │ │
│  │  • Feedback from previous failed attempt (if retry)  │ │
│  └─────────────────────────────────────────────────────┘ │
│  ┌─────────────────────────────────────────────────────┐ │
│  │  EMERGENT CONTEXT (created during the run)           │ │
│  │  • Generated task artifacts                          │ │
│  │  • Tool results (verify_code output, test results)   │ │
│  │  • Agent's self-correction reasoning                 │ │
│  │  • "I tried X, it failed because Y, now trying Z"   │ │
│  └─────────────────────────────────────────────────────┘ │
│                                                           │
│  Phase 1 total: ~15-25K tokens (well within any window)  │
│  Phase 4 (with customer context + feedback): ~30-50K     │
└───────────────────────────────────────────────────────────┘
```

**Static context** — Doesn't change between runs. Loaded once.
- Task type guidelines ("what makes a good DEBUG task")
- Proficiency level definitions ("INTERMEDIATE means 3-5 years experience, expects multi-file solutions")
- Output schema requirements
- Verification checklist
- The agent's behavioral instructions

**Per-request context** — Changes every run. Assembled by the orchestrator or by agent tools.
- Competency scope (from Supabase)
- Customer/org preferences (from Supabase)
- Relevant scenarios (from scenario files or generated)
- Specific requirements from the user ("focus on observability", "20 minute time constraint")
- Feedback from a previous failed attempt

**Emergent context** — Created during the run. Accumulated in the conversation.
- Tool results (verification output, test results)
- The agent's own reasoning and intermediate decisions
- Self-correction history ("I tried X, it failed because Y, so I'm trying Z")

**The Phase 1 approach (simple, sufficient):**

For Phase 1, context engineering is straightforward because each agent is short-lived:

```
Generator agent receives:
  System prompt:        behavioral instructions (static, ~1K tokens)
  + Domain knowledge:   guidelines for this task type + tech stack (static, ~2K tokens)
  + Competency scope:   from Supabase (per-request, ~500 tokens)
  + Requirements:       user's specific asks (per-request, ~500 tokens)
  + Scenario:           selected or generated scenario (per-request, ~500 tokens)
  = ~4.5K tokens of context before the agent starts generating

  During the run:
  + Generated task (~5-10K tokens)
  + Tool results (~1-2K tokens per tool call)
  + Self-correction reasoning (~1-2K per fix)
  = ~15-25K tokens total for a successful run with 1-2 corrections

  Well within any context window. No management needed.
```

The eval agent gets even less — just the generated task + the eval rubric. Fresh context, no history from generation. It can't be biased by the generator's reasoning because it never sees it.

**What changes at scale (Phase 3-4):**

When we add customer context, feedback history, cross-task deduplication, and multi-step generation for complex task types, context management becomes real work:

- **Retrieval**: Before generation, query Supabase for relevant customer feedback ("their last 3 tasks were rated low because 'too many files'" → inject as a constraint). Use embedding similarity to find RELEVANT feedback, not all feedback.
- **Compression**: If the self-correction loop runs long (10+ turns for a complex MANAGE INFRA task), older tool results can be summarized. "Previously: Docker build failed due to missing dependency, fixed. Compose up failed due to port conflict, fixed." instead of the full 5K tokens of Docker error output.
- **Selective inclusion**: The agent doesn't need ALL guidelines for ALL task types. Load only the guidelines for the specific task type and tech stack being generated. This is obvious but easy to get wrong when you have 50+ guideline documents.
- **Memory across runs**: If the system generates 10 tasks in a batch, later tasks should know about earlier tasks (for deduplication, for variety). This is short-term batch memory, stored in the Supabase run state.

**The principle that stays constant across all phases: context is curated, not accumulated.** The agent sees what it needs, when it needs it, at the right level of detail. Everything else is available via tools if the agent decides it's relevant — but not pre-loaded "just in case."

---

### The Path from POC to Production

```
Phase 1 (POC):
  BUILD tasks with self-correction → answers model + framework questions
                                          │
Phase 2 (Foundation):                     ▼
  Add DESIGN REVIEW + DEBUG    → answers task type transferability
  Add verification tools       → answers self-correction effectiveness
  Add Supabase state tracking  → answers cost economics
  Start human rating dataset   → builds toward DSPy + auto-approval
                                          │
Phase 3 (Scale):                          ▼
  Customer context injection   → answers context relevance
  Deduplication                → answers similarity thresholds
  Confidence-based auto-approve→ answers human-in-the-loop calibration
  100 tasks/day target         → answers deployment pipeline readiness
                                          │
Phase 4 (Customer-Facing):               ▼
  API for org-triggered generation → answers intake agent design
  Per-org preferences          → answers customer context value
  DSPy optimization            → answers prompt optimization ROI
  Feedback loop                → begins self-improvement cycle
```

Each phase answers the questions that unlock the next phase. We don't need to decide everything now — we need to build Phase 1 and let the experiments guide the rest.

---

## Appendix: Task Type Generation Patterns

| Task Type | Phases | Key Artifacts | Verification Tools Needed |
|-----------|--------|---------------|--------------------------|
| **BUILD** | Single-phase (3-turn conversation) | Starter code, answer code, README | parse_code, run_tests, check_deployability |
| **DEBUG** | Two-phase (correct system → inject bugs) | Buggy code, failing tests, error logs, answer key | parse_code, run_tests (must fail on buggy, pass on fixed), check_deployability |
| **DESIGN REVIEW** | Single-phase (doc with intentional gaps) | Design doc (markdown), answer key | Structure check only (no code) |
| **PR REVIEW** | Two-phase (base repo → flawed PR) | Base repo, PR branch, answer key | parse_code (PR files), validate PR structure |
| **UX / CRITICAL THINKING** | Template + AI scenario | Figma template, product scenario, rubric | Structure check only |
| **MANAGE INFRA** | Two-phase (working configs → broken configs) | Infra configs, error logs, answer key | validate_dockerfile, docker_compose_up, validate_k8s_manifest |
