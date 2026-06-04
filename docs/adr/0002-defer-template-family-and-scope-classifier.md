# 2. Defer the Python template family + scope-driven classifier past v1

Date: 2026-06-02
Status: Accepted

## Context

`docs/plans/2026-06-01-platform-prereqs.md` lists two platform changes as prerequisites
for new task categories: a Python **template family** (`python-base → web/data/ai-agent`)
and **scope-driven classification**. That doc also notes the two are coupled: *"a second
template is what makes scope-driven matching necessary, so they ship as one unit."*

Today there is exactly one Python template (`utkrusht-python`, the fat image — plus a
`python-sql` variant that currently mis-declares the same `template_id`, a latent bug).
That image already bundles `langchain / llama-index / openai / anthropic` and supports
per-task `requirements.txt` top-up at gate time. The existing classifier routes by
competency name + capability sheets.

## Decision

Defer **both** the template family and scope-driven classification past v1. v1 runs on
the existing `utkrusht-python` image + per-task `requirements.txt` (for the ~6 agent
frameworks) + the existing name/capability classifier (which routes Python-ish
competencies to the only Python template by default).

Build the template family + scope classifier **only when** one of these actually bites:
(a) per-task framework install at gate time is too slow, or (b) a genuine dependency
conflict forces isolating the agent pins. The plan's open "dependency-conflict" question
collapses into a one-line Phase-A smoke test: *does pip-installing the 6 frameworks on
`utkrusht-python` build green and run the reference?*

Keep only the trivially-safe, independent platform change: stop stamping `task_intent`
(no reader exists).

## Consequences

- An entire cross-cutting workstream (family build, manifest composition, the open
  sibling-FROM vs `from_template()` mechanism choice, the duplicate-`template_id`
  cleanup, the scope classifier change + `registry_version` bump) leaves v1's critical
  path.
- The first agent task ships on infrastructure that already exists.
- Reverses `platform-prereqs.md`'s sequencing — that doc should be annotated to say the
  prereqs are demand-driven, not upfront, for this category.
- If the Phase-A smoke test reveals a real conflict, the family is pulled back in — this
  decision is reversible by design.

## Alternatives considered

- **Build prereqs first (as planned)** — rejected for v1: speculative work for a
  one-template world where scope-driven routing has nothing to disambiguate.
- **Scope classifier now, family later** — rejected: scope-driven routing is a no-op
  while only one Python template exists.
