# Design Review Flow — Design Spec

## Overview

A new task category for UI/UX design assessments. Candidates receive a Figma file with intentionally injected UX flaws, a brief with change requests, and must submit a modified Figma link + written rationale. Evaluation uses an LLM-generated rubric.

## End-to-End Flow

1. **Curate** Figma Community files (CC BY 4.0) into `figma_library.json`, including layer/frame names
2. **Export layer tree** from Figma (via REST API or manual export) and store alongside library entry
3. **CLI: `python -m design_review_flow generate`** — LLM generates flaw injection spec, candidate brief, and evaluation rubric (using layer tree for accurate element references)
4. **LLM eval gate** validates the generated flaw spec (retry on failure)
5. **Human** duplicates the community file in Figma
6. **Figma Plugin** reads flaw spec JSON, matches elements by exact layer name, applies changes automatically
7. **Human** creates a duplicate link for the flawed file
8. **CLI: `python -m design_review_flow store`** — stores task in Supabase
9. **Candidate** receives Figma duplicate link + brief, submits modified Figma link + written rationale
10. **Evaluator** scores submission using rubric + answer key

## Component 1: Figma Community File Library

JSON registry at `design_review_flow/figma_library.json`.

```json
[
  {
    "id": "lib-001",
    "name": "SaaS Dashboard - Analytics",
    "figma_community_url": "https://figma.com/community/file/...",
    "domain": "saas",
    "screens": ["dashboard", "settings", "user-profile", "onboarding"],
    "frames": {
      "dashboard": {
        "frame_name": "Dashboard / Main",
        "key_elements": {
          "sidebar_nav": "Sidebar / Nav Labels",
          "primary_cta": "Dashboard / Header / CTA Button",
          "metric_cards": "Dashboard / Metrics / Card Group"
        }
      },
      "onboarding": {
        "frame_name": "Onboarding / Step 1",
        "key_elements": {
          "primary_cta": "Onboarding / Step 1 / Get Started Button",
          "progress_bar": "Onboarding / Progress Indicator",
          "heading": "Onboarding / Step 1 / Title"
        }
      }
    },
    "layer_tree_file": "layer_trees/lib-001.json",
    "complexity": "intermediate",
    "license": "CC BY 4.0",
    "attribution": "Author Name"
  }
]
```

**Domains:** Healthcare, Fintech, E-commerce, SaaS, EdTech, Social Media, Travel, Food Delivery, Fitness, Productivity.

**Selection criteria:**
- CC BY 4.0 license
- Multi-screen (3-4+ screens)
- Clean, well-structured/named layers (so plugin can match by exact name)
- Realistic designs

**Layer tree export:** When curating a file, export the Figma layer tree (via Figma REST API `GET /v1/files/:key`) and save as `design_review_flow/layer_trees/{id}.json`. This gives the LLM actual element names to reference in flaw specs.

Curation is manual — someone browses Figma Community, adds entries, and records layer/frame names.

## Component 2: LLM Flaw Injection Spec Generation

**Input:** Competency, proficiency level, scenario, library entry (including `frames` and layer tree).

The LLM receives the actual layer tree so it can reference real element names — not guess.

**LLM output:**

```json
{
  "source_file": "lib-001",
  "target_screens": ["onboarding", "dashboard"],
  "flaws": [
    {
      "id": "flaw-1",
      "screen": "onboarding",
      "type": "visual_hierarchy",
      "severity": "major",
      "instruction": "Reduce the primary CTA button size to match secondary buttons and change text from 'Get Started' to 'Continue'",
      "target_layer": "Onboarding / Step 1 / Get Started Button",
      "rationale": "Breaks visual hierarchy — user can't distinguish primary action"
    },
    {
      "id": "flaw-2",
      "screen": "dashboard",
      "type": "accessibility",
      "severity": "minor",
      "instruction": "Change the sidebar text color to #999999 on #f5f5f5 background",
      "target_layer": "Sidebar / Nav Labels",
      "rationale": "Fails WCAG AA contrast ratio (2.8:1 instead of 4.5:1)"
    }
  ],
  "answer_key": {
    "flaws_summary": "2 flaws injected across 2 screens",
    "expected_findings": [
      "CTA lacks visual prominence — no clear primary action",
      "Sidebar text fails accessibility contrast requirements"
    ],
    "overall_quality": "poor — critical UX and accessibility issues"
  }
}
```

Note: `element_hint` replaced with `target_layer` — exact Figma layer name from the library entry.

**Flaw categories:**
- Visual hierarchy (size, weight, placement)
- Accessibility (contrast, touch targets, screen reader hints)
- Information architecture (confusing navigation, wrong grouping)
- Copy/microcopy (vague CTAs, misleading labels, missing error states)
- Consistency (mixed patterns, inconsistent spacing/colors)
- User flow (dead ends, unnecessary steps, confusing sequences)

**Proficiency scaling:**
- Beginner: 2-3 obvious flaws, single screen
- Basic: 3-4 flaws, mix of obvious and subtle
- Intermediate: 4-6 flaws across multiple screens, mostly subtle
- Advanced: 6-8 subtle flaws, some requiring flow-level thinking

## Component 3: Evaluation Gate

Follows the same pattern as `pr_review_flow/pr_review_evals.py` and `evals.py`.

**What it validates:**

1. **Flaw spec eval:**
   - Every `target_layer` in the flaw spec exists in the library entry's layer tree
   - Flaw types are from the allowed categories
   - Flaw count matches proficiency scaling (e.g., beginner shouldn't have 8 flaws)
   - Instructions are actionable (specific enough for the plugin to apply)
   - Flaws are distinct (no duplicates targeting the same element)
   - Rationale explains a real UX principle violation

2. **Brief eval:**
   - `change_requests` don't leak the answer key (no mention of specific flaws)
   - Domain context is coherent with the library entry's domain
   - Constraints are specific and testable
   - Mix of critique/redesign matches proficiency level

3. **Rubric eval:**
   - All criteria have clear scoring descriptions
   - Weights sum to 100

**Retry behavior:** On failure, feed eval feedback back to LLM and regenerate. Max retries: 3 (configurable via `MAX_EVAL_RETRIES`).

## Component 4: Candidate Brief Generation

**LLM generates the candidate-facing brief:**

```json
{
  "title": "UX Review: FinTrack Dashboard Onboarding",
  "domain_context": "FinTrack is a personal finance app targeting millennials. They recently redesigned their onboarding flow and dashboard based on user feedback about drop-off rates.",
  "constraints": [
    "Must follow WCAG AA accessibility standards",
    "Mobile-first design (375px primary viewport)",
    "Brand uses Inter font family, blue (#2563EB) as primary"
  ],
  "change_requests": [
    {
      "type": "critique",
      "prompt": "Review the onboarding flow and identify any UX issues that could cause user drop-off"
    },
    {
      "type": "redesign",
      "prompt": "Reimagine the dashboard layout to better surface savings goals"
    }
  ],
  "submission_requirements": {
    "figma_link": "Share your modified Figma file link",
    "written_rationale": "For each change, explain your reasoning (max 200 words per change)"
  },
  "time_limit_minutes": 45
}
```

**Mix per proficiency:**
- Beginner: mostly "critique" (find the issues)
- Basic: critique + small fixes
- Intermediate: critique + redesign of specific components
- Advanced: full flow reimagination + rationale

## Component 5: Figma Plugin

**Tech:** TypeScript, Figma Plugin API.

**How it works:**
1. User opens a duplicated community file in Figma
2. Launches the plugin
3. Pastes the flaw injection spec JSON
4. Plugin parses instructions and matches elements by **exact layer name** (`target_layer` field)
5. Shows preview of matched elements — human confirms
6. Applies changes automatically
7. Outputs a summary log (applied vs. needs manual action)

**Automated modification capabilities:**

| Flaw Type | Plugin Action |
|-----------|--------------|
| Copy/microcopy | Change text content on matching text nodes |
| Accessibility (contrast) | Modify fill colors on target elements |
| Visual hierarchy (size) | Resize elements, change font size/weight |
| Consistency (spacing) | Adjust padding, margins, alignment |
| Consistency (colors) | Swap fills to break color system |
| Visual hierarchy (placement) | Reorder or reposition elements |

**Element matching strategy (v1):**
- Match by **exact layer name** only (from `target_layer` field)
- If a layer name is not found, report it as "needs manual action"
- No fuzzy matching in v1 — accuracy over convenience

**Limitations (require manual intervention):**
- Complex layout restructuring
- Adding new screens or components from scratch
- Deleting flows or interactions
- Any flaw where `target_layer` can't be matched

**Plugin build/distribution:**
- Built with TypeScript, compiled to JS
- Distributed as a private Figma plugin (requires Figma developer account)
- `manifest.json` contains plugin ID registered on Figma's developer platform

## Component 6: Evaluation Rubric

**LLM generates alongside the flaw spec.**

```json
{
  "criteria": [
    {
      "name": "Flaw Identification",
      "weight": 30,
      "scoring": {
        "excellent": "Identified all injected flaws with correct reasoning",
        "good": "Identified 70%+ of flaws",
        "acceptable": "Identified 40-70% of flaws",
        "poor": "Identified less than 40%"
      }
    },
    {
      "name": "Design Changes Quality",
      "weight": 30,
      "scoring": {
        "excellent": "Changes directly address the issues, follow UX best practices",
        "good": "Changes mostly address issues, minor gaps",
        "acceptable": "Some changes relevant but inconsistent",
        "poor": "Changes don't address core issues"
      }
    },
    {
      "name": "Written Rationale",
      "weight": 25,
      "scoring": {
        "excellent": "Clear reasoning grounded in UX principles, references constraints",
        "good": "Solid reasoning with minor gaps",
        "acceptable": "Surface-level reasoning",
        "poor": "No clear reasoning or contradicts UX principles"
      }
    },
    {
      "name": "Design Consistency",
      "weight": 15,
      "scoring": {
        "excellent": "Changes maintain visual consistency, respect brand constraints",
        "good": "Mostly consistent with minor deviations",
        "acceptable": "Some inconsistencies introduced",
        "poor": "Changes break the existing design system"
      }
    }
  ],
  "bonus_points": "Candidate identified additional legitimate UX issues beyond injected flaws"
}
```

**Evaluation flow:**
1. Human evaluator opens candidate's Figma link
2. Compares against answer key
3. Reads written rationale
4. Scores using rubric

Automated LLM scoring of the written rationale is deferred to v2.

## Component 7: Supabase Storage

Same `tasks` table, `task_type: "design_review"`. Schema follows existing patterns from `pr_review_flow`.

**Top-level fields (matching existing flows):**

```json
{
  "task_id": "uuid",
  "task_type": "design_review",
  "task_blob": {
    "title": "UX Review: FinTrack Dashboard Onboarding",
    "task_type": "design_review",
    "domain_context": "...",
    "constraints": ["..."],
    "change_requests": ["..."],
    "figma_source_link": "https://figma.com/community/file/...",
    "figma_flawed_link": "https://figma.com/file/...?duplicate",
    "attribution": "Original Author, CC BY 4.0",
    "time_limit_minutes": 45,
    "short_overview": "...",
    "outcomes": "...",
    "question": "..."
  },
  "solutions": {
    "flaw_spec": {},
    "answer_key": {},
    "evaluation_rubric": {}
  },
  "eval_info": {
    "flaw_spec_eval": { "passed": true, "feedback": "..." },
    "brief_eval": { "passed": true, "feedback": "..." },
    "rubric_eval": { "passed": true, "feedback": "..." }
  },
  "criterias": [{"name": "UI/UX Design", "proficiency": "INTERMEDIATE", "competency_id": "uuid"}],
  "readme_content": null,
  "is_shared_infra_required": false,
  "is_deployed": false
}
```

**Key differences from coding tasks:**
- `flaw_spec`, `answer_key`, `evaluation_rubric` stored in `solutions` (not in `task_blob`) — keeps candidate-visible data separate from internal data
- `readme_content` is null (no GitHub repo)
- `is_shared_infra_required` is always false
- `is_deployed` is always false

**`task_competencies` insert:** After task creation, insert into `task_competencies` junction table (same as PR review flow).

## Component 8: CLI Commands

Entry point: `design_review_flow/__main__.py` (invoked via `python -m design_review_flow`).

### `generate`
```bash
python -m design_review_flow generate \
  --competency path/to/competency.json \
  --proficiency INTERMEDIATE \
  --scenario "SaaS onboarding redesign" \
  --library-entry-id lib-001 \
  --env dev \
  --dry-run
```

**Steps:**
1. Load library entry from `figma_library.json`
2. Load layer tree from `layer_trees/{id}.json`
3. Call LLM to generate flaw spec + brief + rubric
4. Run eval gate (retry up to `MAX_EVAL_RETRIES` on failure)
5. Save output JSON to `infra_assets/design_tasks/{timestamp}_{library_id}/`
6. Print path to generated spec

**Output file:** `infra_assets/design_tasks/{timestamp}_{library_id}/design_task_spec.json`

Contains: flaw spec, candidate brief, evaluation rubric, library entry metadata.

**Flags:**
- `--env` (`dev`/`prod`) — which Supabase environment (for competency lookup)
- `--dry-run` — generate and eval but don't save to disk

### `store`
```bash
python -m design_review_flow store \
  --spec-file infra_assets/design_tasks/.../design_task_spec.json \
  --figma-link "https://figma.com/file/...?duplicate" \
  --env dev
```

**Steps:**
1. Load the generated spec file
2. Validate the spec file exists and is well-formed
3. Validate the Figma link format
4. Construct Supabase record (task_blob + solutions + eval_info)
5. Insert into `tasks` table
6. Insert into `task_competencies` table
7. Print task_id

**Flags:**
- `--env` (`dev`/`prod`) — which Supabase environment to store in

**Two-command split rationale:** There is a mandatory manual step between generate and store (running the Figma plugin + creating the duplicate link). The intermediate state is the JSON file on disk.

## Component 9: Error Handling

| Scenario | Handling |
|----------|----------|
| LLM generates flaws for non-existent layers | Eval gate catches this (validates `target_layer` against layer tree) |
| Plugin can't match a layer name | Plugin reports "needs manual action" in summary log |
| `store` called with stale/invalid spec file | Validate spec file schema before inserting |
| Figma duplicate link becomes invalid | Out of scope — link validity is the curator's responsibility |
| Eval gate fails 3 times | Stop and print error with feedback from last eval |

## File Structure

```
design_review_flow/
├── __init__.py
├── __main__.py                  # CLI entry point (Click)
├── design_review_multiagent.py  # Main orchestrator
├── prompts.py                   # System + generation prompts
├── schemas.py                   # JSON schemas for structured LLM output
├── design_review_evals.py       # Eval logic for flaw spec quality
├── figma_library.json           # Curated community file registry
├── layer_trees/                 # Exported Figma layer trees per library entry
│   └── lib-001.json
└── figma_plugin/
    ├── manifest.json            # Figma plugin manifest
    ├── code.ts                  # Plugin logic
    ├── ui.html                  # Plugin UI
    ├── package.json
    └── tsconfig.json
```

## Dependencies

- No new Python dependencies — uses existing OpenAI/Portkey, Supabase, Click
- Figma plugin: TypeScript, Figma Plugin API (no external npm dependencies needed)
- Figma developer account required for plugin registration

## What's Manual vs Automated

| Step | Manual | Automated |
|------|--------|-----------|
| Curate Figma Community files + record layer names | ✓ | |
| Export layer tree (Figma REST API) | ✓ (one-time per file) | |
| Generate flaw spec + brief + rubric | | ✓ (LLM) |
| Eval gate on generated output | | ✓ (LLM) |
| Duplicate community file in Figma | ✓ | |
| Apply flaws via plugin | Trigger plugin | Plugin applies changes |
| Create duplicate link | ✓ | |
| Store task in Supabase | | ✓ (CLI) |
| Evaluate candidate submission | ✓ (human reviewer) | |
