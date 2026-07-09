# flows/design_review — reserved

The design-review flow (UI/UX assessments with Figma flaw injection) is **not
currently implemented in code** — its modules were removed before the 2026-07-07
flows-restructure. This folder reserves the name so a re-implementation slots in
symmetrically with the other flows (`tech`, `pr_review`, `non_tech`).

If you re-add it, follow the flow contract in `docs/ARCHITECTURE.md`: a
`__main__.py` entry, stages under `stages/` if multi-stage, and imports only from
`flows/_base`, `infra/`, and `task_generation_prompts/` — never a sibling flow.

Historical design: `docs/plans/2026-03-30-design-review-flow.md`.
