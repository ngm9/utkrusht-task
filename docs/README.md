# Docs

Layout map for `docs/`. Each folder owns one concern; cross-links are relative.

## Layout

```
docs/
├── README.md                    you are here
│
├── autonomous-task-agent/       multi-agent orchestrator architecture
├── deployment/                  DigitalOcean / E2B deploy infrastructure
├── eval-system/                 LLM eval critics + E2B build/test gate
├── prompt-generator/            DSPy prompt-template generator + agent
├── task-builder/                conversational web frontend (FastAPI)
├── task-classifier/             LLM classifier + Supabase combo cache + templates
│
├── plans/                       implementation plans (one per feature/change, dated)
├── specs/                       design specs (one per feature, dated)
│
└── drawings/                    all excalidraw + diagrams, organized per feature
    ├── deployment/
    │   └── infrastructure.excalidraw
    ├── prompt-generator/
    │   ├── agent.excalidraw
    │   └── architecture.excalidraw
    └── task-classifier/
        └── classifier-flow.excalidraw
```

## Conventions

- **Feature folders** (`autonomous-task-agent/`, `task-classifier/`, …) hold *current-state* reference docs: how the system works now. Markdown + HTML mirror where helpful.
- **`plans/`** holds dated implementation plans (`YYYY-MM-DD-<slug>.md`). Each plan links to its spec.
- **`specs/`** holds dated design specs (`YYYY-MM-DD-<slug>-design.md`). One spec per plan.
- **`drawings/`** holds all Excalidraw files, mirrored under feature subfolders so the diagram lives next to its sibling docs by name.
- HTML files include scrollspy + a sticky sidebar TOC. Open them in a browser to navigate large docs.
- Excalidraw files: drag-and-drop onto [excalidraw.com](https://excalidraw.com) or open via `File → Open`.

## Where things moved (2026-05-26)

| Old path | New path |
|---|---|
| `docs/superpowers/plans/*.md` | `docs/plans/*.md` |
| `docs/superpowers/specs/*.md` | `docs/specs/*.md` |
| `docs/deployment/infrastructure.excalidraw` | `docs/drawings/deployment/infrastructure.excalidraw` |
| `docs/prompt-generator/agent.excalidraw` | `docs/drawings/prompt-generator/agent.excalidraw` |
| `docs/prompt-generator/architecture.excalidraw` | `docs/drawings/prompt-generator/architecture.excalidraw` |
| `docs/task-classifier/classifier-and-templates.{md,html}` | deleted — split into `classifier.{md,html}` + `e2b-templates.{md,html}` |

## Adding a new doc

- New feature reference doc → make a folder under `docs/<feature>/` with `<topic>.md` (+ `<topic>.html` if it has long-form structure).
- New plan → `docs/plans/YYYY-MM-DD-<slug>.md`, link to its spec.
- New spec → `docs/specs/YYYY-MM-DD-<slug>-design.md`.
- New diagram → `docs/drawings/<feature>/<topic>.excalidraw`.
