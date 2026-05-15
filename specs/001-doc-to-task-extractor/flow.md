# Flow & Architecture

This document describes **how the extractor works** — the architecture, the
agent loop, the tool surface, and the end-to-end data flow.

For the **why this approach** (decisions and rejected alternatives), see
[`research.md`](./research.md). For the **what we're building**, see
[`spec.md`](./spec.md). For the **comparison with today's manual flow**,
see [`current-state.md`](./current-state.md).

## One-paragraph architecture

A new sub-package `task_input_parser/` (sibling to `non_tech_flow/`, `pr_review_flow/`)
invoked as `python -m task_input_parser <brief-path>`. Python deterministically parses
the input into a structured AST, hands it to a single LLM call with function
calling enabled, and dispatches tool requests as the agent makes them. The
agent decides task boundaries, fetches resources via tools, and emits
per-task markdown into `tmp/extract_<timestamp>/`. No external writes outside
of resource fetches the agent explicitly initiates.

## End-to-end data flow

```
┌────────────────────────────────────────────────────────────────────────┐
│ INPUT: brief.docx / brief.md / brief.txt                                │
└─────────────────────────────────┬──────────────────────────────────────┘
                                   │
                                   ▼
                ┌────────────────────────────────────┐
                │  task_input_parser/cli.py:main                 │
                │  - parse CLI args                   │
                │  - create tmp/extract_<timestamp>/  │
                │  - initialize cost accumulator      │
                │  - call into task_input_parser.ast then agent  │
                └─────────────────┬──────────────────┘
                                   │
                                   ▼
                ┌────────────────────────────────────┐
                │  task_input_parser/ast.py                      │
                │  Parse the brief into a structured  │
                │  AST. Deterministic.                │
                │   - .docx → python-docx + zipfile   │
                │   - .md   → markdown-it-py          │
                │   - .txt  → plain read              │
                │  Output: BriefAST                   │
                │  (sections, paragraphs, tables,     │
                │   embedded images, external URLs,   │
                │   code fences)                      │
                └─────────────────┬──────────────────┘
                                   │
                                   ▼
                ┌────────────────────────────────────┐
                │  task_input_parser/agent.py                    │
                │  Single Portkey call to Claude      │
                │  Sonnet with function-calling.      │
                │  Loops on tool requests:            │
                │                                     │
                │    LLM thinks: "this brief has 2    │
                │      tasks: a MySQL one and a       │
                │      frontend one"                  │
                │    LLM calls: process_image(...)    │
                │    LLM calls: fetch_external_code(...)│
                │    LLM calls: emit_task(slug=...,   │
                │                        markdown=...)│
                │    LLM stops.                       │
                │                                     │
                │  After every LLM response:          │
                │   - record cost                     │
                │   - abort if cost > $2 cap          │
                └─────────────────┬──────────────────┘
                                   │
                                   ▼
                ┌────────────────────────────────────┐
                │  OUTPUT:                            │
                │  tmp/extract_<timestamp>/           │
                │   ├── task-1-<slug>.md              │
                │   ├── task-2-<slug>.md              │
                │   ├── run.log                       │
                │   └── cost.json                     │
                └────────────────────────────────────┘
```

The orchestration is intentionally thin. The Python wrapper opens the file,
parses, hands the agent the AST + tools, and runs the loop. All the
"intelligence" lives in the agent's system prompt and the tools the agent
can call.

## The agent loop in detail

```python
# task_input_parser/agent.py — pseudocode (~30 lines)
from .cost import CostAccumulator
from .tools import all_tools, dispatch

SYSTEM_PROMPT = Path(__file__).parent / "prompts" / "system.md"

def run(ast: BriefAST, output_dir: Path, cost: CostAccumulator) -> RunSummary:
    portkey = init_portkey_client()
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT.read_text()},
        {"role": "user",   "content": format_ast_as_user_message(ast)},
    ]
    emitted, inline_notes = [], 0

    while True:
        response = portkey.chat.completions.create(
            model="claude-sonnet-4-6",
            messages=messages,
            tools=all_tools(),                 # 3 Pydantic schemas → JSON-schema
            tool_choice="auto",
            max_tokens=8192,
        )
        cost.add(response.usage); cost.check_or_abort()

        msg = response.choices[0].message
        messages.append(msg.model_dump())

        if msg.stop_reason in ("end_turn", "stop") and not msg.tool_calls:
            break

        for tc in msg.tool_calls or []:
            try:
                result = dispatch(tc.function.name, tc.function.arguments, output_dir)
                if tc.function.name == "emit_task":
                    emitted.append(result.written_to)
                    inline_notes += result.inline_note_count  # counted by emit_task
                messages.append({"role": "tool", "tool_call_id": tc.id,
                                  "content": result.model_dump_json()})
            except Exception as e:
                messages.append({"role": "tool", "tool_call_id": tc.id,
                                  "content": json.dumps({"error": str(e)})})

    return RunSummary(emitted_tasks=emitted, inline_notes=inline_notes, total_cost=cost.total())
```

That's the whole orchestrator. **Everything else lives in the system prompt
or in tools.**

## The three tools the agent can call

| Tool | What it does | Implementation summary |
|---|---|---|
| `process_image(image_ref)` | Extracts an image from the source doc, uploads it to the shared Drive `task-resources/` folder, returns Drive thumbnail URL + view URL + basic metadata (width, height, content-hash). **No vision-LLM analysis** — image understanding by downstream consumers is out of scope. | `zipfile` for `.docx` extraction; existing `non_tech_flow/google_utils.py` for Drive upload. Drive upload result cached by `sha256(image_bytes)` so the same image bytes deduplicate to one Drive file across re-runs and across task references within a brief. |
| `fetch_external_code(url)` | Detects the platform from URL pattern; for GitHub Gist (the only v1-supported platform) fetches via the public Gists API and returns `{filename: source_content}` plus a `platform_detected` field. For CodePen URLs (Cloudflare-gated) returns `status="bot_protected"` with the canonical operator-facing message. For other platforms returns `status="platform_not_supported"`. **No bot-protection bypass is attempted under any condition** (constitution Principle V). | Gist: plain HTTP via `https://api.github.com/gists/<id>`. CodePen + others: structured non-OK status only; the agent emits an inline `**Note:**` in the affected task's markdown. Result cached by `sha256(url)`. |
| `emit_task(slug, markdown_content)` | Writes the final per-task markdown to `tmp/extract_*/task-N-slug.md`. Runs the leak-check regex BEFORE writing; rejects on any banned domain match. Counts the inline `**Note:**` entries in the markdown and returns the count to the agent so the run summary can reflect them. | The leak check is the safety gate for constitution Principle VIII. If the markdown contains `codepen.io`, `codesandbox.io`, etc., the tool returns a structured error to the agent (the agent retries with the URL removed). |

All three tools have Pydantic input/output schemas. The agent sees these
schemas via Portkey's function-calling format and never needs platform-
specific or implementation-specific knowledge.

When the LLM encounters genuine ambiguity it can't resolve (e.g., a query
references a column not defined in any table), it includes an inline
`**Note:**` paragraph in the relevant section of the emitted markdown and
proceeds. The operator reviewing the markdown sees the note in place. There
is no separate gap-tracking file.

## The system prompt — the agent's brain

Located at `task_input_parser/prompts/system.md`. The Python wrapper is intentionally
"dumb" — the prompt is where the agent's behaviour is defined. The prompt
covers:

1. **Role.** "You are an assessment-task extraction agent. Given a parsed
   brief AST, you produce per-task markdown."
2. **Task definition.** What counts as one task (self-contained scenario +
   requirements + evaluation criteria).
3. **Procedure.** Read the whole AST first → decide N tasks → for each task
   call the tools you need → call `emit_task` once per task → stop.
4. **Tool contracts.** When to call each tool, what to expect back, what
   failures look like.
5. **Markdown output requirements.** Section order (Task Overview → **Role Description** (optional) → Business Context → Schema/Requirements → Functional Requirements → Resources → Evaluation Criteria), the inline-image-embed format, the starter-code-block format.
6. **Role description extraction.** If the brief contains role-introducing prose (target seniority, years of experience, must-have skills, team context), reproduce that prose in a `## Role Description` section in **every** emitted task markdown. If the brief contains no role description, omit the section entirely (no heading, no placeholder).
7. **Prohibitions.** Never invent missing information. Never reference the source URL of any scraped resource. When the LLM cannot resolve ambiguity, it emits an inline `**Note:**` paragraph in the relevant markdown section rather than guessing silently.
8. **Termination.** Stop only when every identified task has been emitted.

The system prompt is the single highest-leverage file in the project —
quality of output is bounded by quality of this prompt.

## Caching strategy

Two caches, both content-addressed, in `tmp/parser_cache/`:

- **Resource cache:** `tmp/parser_cache/<sha256(url)>.json` records the
  result of `fetch_external_code`. Cache hits skip the network round-trip.
  Failed fetches and `bot_protected` / `platform_not_supported` outcomes
  are also cached so dead URLs don't trigger repeat work on every re-run.
- **Image-upload cache:** `tmp/parser_cache/<sha256(image_bytes)>.drive.json`
  records the Drive URL set returned by `process_image`. Same image bytes
  resolve to one Drive file across tasks and across re-runs (no second
  upload).

Within-run idempotency is the v1 promise. Cross-run idempotency (same brief
on different days → same `tmp/extract_*/` output) is deferred — each run
gets a fresh timestamped directory.

## Cost discipline

`task_input_parser/cost.py` accumulates LLM cost across every Portkey call:

```python
@dataclass
class CostAccumulator:
    cap_usd: float = 2.00
    total_usd: float = 0.0
    by_model: dict[str, dict] = field(default_factory=dict)

    def add(self, usage, model): ...
    def check_or_abort(self):
        if self.total_usd > self.cap_usd:
            raise CostCapExceeded(f"$ cap {self.cap_usd:.2f} exceeded — current ${self.total_usd:.4f}. Aborting.")
    def total(self): ...
```

Called after every LLM response. Cap
breach aborts with a clear error; the CLI catches at the top, writes
`cost.json`, exits non-zero.

## What lives where (cheat table)

| Question | Code lives in |
|---|---|
| How does it parse `.docx` / `.md` / `.txt`? | `task_input_parser/ast.py` |
| How does the agent loop? | `task_input_parser/agent.py` (~30 lines of orchestration) |
| What does the agent know about the task? | `task_input_parser/prompts/system.md` |
| How does it extract images from `.docx`? | `task_input_parser/tools/image.py` (uses `zipfile`) |
| How does it upload images to Drive? | `task_input_parser/tools/image.py` (wraps `non_tech_flow/google_utils.py`) |
| How does it handle a design image? | `task_input_parser/tools/image.py` extracts + uploads to Drive; no vision analysis. The downstream consumer follows the Drive link to view the image. |
| How does it extract a role description? | LLM does it as part of `emit_task` content composition (no separate tool); system prompt instructs the LLM to scan for role-introducing prose and emit a `## Role Description` section when found |
| How does it fetch Gist source? | `task_input_parser/tools/fetch.py` + `task_input_parser/tools/scrape/gist.py` (plain HTTP via the public Gists API) |
| What about CodePen / other bot-protected platforms? | `task_input_parser/tools/fetch.py` returns `status="bot_protected"` immediately; no bypass is attempted. The agent emits an inline `**Note:**` asking the operator to paste manually. (Per constitution Principle V.) |
| How does it stay under $2? | `task_input_parser/cost.py` accumulator with cap-and-abort |
| How does it prevent source-URL leaks? | `task_input_parser/leak_check.py` (shared module); `emit_task` runs it before writing |
| How does it flag uncertainty? | The LLM includes an inline `**Note:**` paragraph in the relevant section of the emitted markdown. No separate gap-tracking file. |
| How does the CLI work? | `task_input_parser/cli.py` (Click `@click.command()`) |

## Constitution alignment (summary)

Full constitution check lives in [`plan.md`](./plan.md). One-line summary
of how this flow honours each applicable principle:

- **I. Small Correct Thing First** — US1 alone is shippable in one
  iteration.
- **II. CLI-First with Plugin Registry** — `python -m task_input_parser` matches the
  existing sub-package convention.
- **III. Portkey Gateway Only** — the agent's LLM call goes through Portkey.
- **V. Local-First Artifact Saving** — output stays in `tmp/`.
- **VI. Determinism & Idempotency** — within-run via content-addressed cache.
- **VII. Pre-flight Validation** — tool I/O via Pydantic schemas.
- **VIII. No Customer-Source Leakage** — `emit_task` runs leak-check
  regex before writing.
- **X. Cost Discipline** — $2 cap enforced in `task_input_parser/cost.py`.
- **XI. DRY** — one `fetch_external_code` tool with internal dispatch,
  not five separate scrapers.

Principles IV (DB safety), IX (preview gate), XII (security defaults), XIII
(process improvement) either don't apply or are satisfied trivially in this
feature's scope. See [`plan.md`](./plan.md) for the full check.
