"""Convert a parser-emitted task markdown into scenario_generator input JSON files.

Usage (one invocation per emitted task):

    python -m task_input_parser.prepare_inputs <task.md> \\
        --stack "MySQL" \\
        --proficiency BASIC \\
        [--env dev] [--force] [--dry-run]

    # Multi-stack example (HTML + JS task)
    python -m task_input_parser.prepare_inputs task-2-frontend-popup.md \\
        --stack "HTML and CSS" --stack "Javascript" \\
        --proficiency BASIC

Produces under task_input_files/:
    input_<slug>/<level>/<md-stem>/
        competency_<slug>_<level>_Utkrusht.json
        background_forQuestions_utkrusht_<slug>_<level>.json
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Optional

import click

# Reuse Supabase / LLM helpers from the existing generate_input_files module
# so there is a single source of truth for auth, pricing, and file conventions.
from generate_input_files.generator import (
    HARDCODED_ORGANIZATION,
    PROFICIENCY_YOE_MAP,
    fetch_competencies_from_db,
    generate_role_context,
    init_openai_client,
    init_supabase,
    sanitize_folder_name,
    write_json_safe,
)

# ── Constants ──────────────────────────────────────────────────────────────────

_BASE_DIR = Path("data") / "generated" / "input_files"

# Best-effort keyword → Supabase competency name mapping.
# Keys are lowercase substrings to search for in the markdown content.
# Values are the exact name strings that exist in the Supabase competencies table.
_KEYWORD_STACKS: list[tuple[list[str], list[str]]] = [
    (["mysql"],                                                    ["MySQL"]),
    (["html", "css", "popup", "webpage", "front-end", "frontend"], ["HTML and CSS", "Javascript"]),
    (["reactjs", "react.js", "react component", "jsx"],           ["ReactJs"]),
    (["playwright"],                                               ["Playwright"]),
    (["postgresql", "postgres"],                                   ["PostgreSQL"]),
    (["php"],                                                      ["PHP"]),
    (["golang", "go lang"],                                        ["Golang"]),
    (["java", "spring boot"],                                      ["Java", "Java - Spring Boot"]),
    (["python", "fastapi"],                                        ["Python - FastAPI"]),
    (["python"],                                                   ["Python"]),
    (["langchain"],                                                ["Langchain"]),
    (["llamaindex"],                                               ["Llamaindex"]),
    (["kafka"],                                                    ["Kafka"]),
    (["mongodb"],                                                  ["MongoDB"]),
    (["nodejs", "node.js"],                                        ["NodeJs"]),
    (["typescript"],                                               ["Typescript"]),
    (["nextjs", "next.js"],                                        ["NextJs"]),
    (["docker"],                                                   ["Docker"]),
]

_SCENARIOS_BY_LEVEL = {
    "basic":        _BASE_DIR / "task_scenarios" / "task_scenarios.json",
    "intermediate": _BASE_DIR / "task_scenarios" / "task_scenarios_intermediate.json",
    "beginner":     _BASE_DIR / "task_scenarios" / "task_scenarios.json",
}


# ── Helpers ────────────────────────────────────────────────────────────────────

def _detect_stacks(md_content: str) -> list[str]:
    """Best-effort stack detection from markdown text. Returns [] if uncertain."""
    lower = md_content.lower()
    for keywords, stacks in _KEYWORD_STACKS:
        if any(kw in lower for kw in keywords):
            return stacks
    return []


def _extract_role_description(md_content: str) -> Optional[str]:
    """Return the prose under '## Role Description' if the section exists."""
    match = re.search(
        r"^##\s+Role\s+Description\s*\n(.*?)(?=^##|\Z)",
        md_content,
        re.MULTILINE | re.DOTALL | re.IGNORECASE,
    )
    if not match:
        return None
    text = match.group(1).strip()
    return text or None


def _output_dir(names: list[str], level: str, md_stem: str) -> Path:
    combined = "_".join(n.lower() for n in names)
    tech_slug = sanitize_folder_name(combined)
    return _BASE_DIR / tech_slug / level / md_stem


# ── CLI ────────────────────────────────────────────────────────────────────────

@click.command()
@click.argument("task_md", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option(
    "--stack", "-s", multiple=True,
    help=(
        "Competency name as it appears in Supabase. "
        "Use multiple flags for multi-stack tasks: "
        "--stack 'HTML and CSS' --stack 'Javascript'. "
        "Omit to attempt auto-detection from the markdown content."
    ),
)
@click.option(
    "--proficiency", "-p", required=True,
    type=click.Choice(["BEGINNER", "BASIC", "INTERMEDIATE", "ADVANCED"], case_sensitive=False),
    help="Proficiency level.",
)
@click.option(
    "--env", default="dev", show_default=True,
    type=click.Choice(["dev", "prod"]),
    help="Supabase environment to look up competencies.",
)
@click.option("--force", is_flag=True, default=False, help="Overwrite existing output files.")
@click.option("--dry-run", is_flag=True, default=False, help="Preview without writing any files.")
def main(
    task_md: Path,
    stack: tuple[str, ...],
    proficiency: str,
    env: str,
    force: bool,
    dry_run: bool,
) -> None:
    """Convert a parser-emitted task markdown into scenario_generator input JSON files.

    TASK_MD is the path to a task-*.md file produced by the parser
    (e.g. tmp/extract_2026-05-14_05-09-43/task-1-mysql.md).
    """
    proficiency = proficiency.upper()
    level = proficiency.lower()
    md_content = task_md.read_text(encoding="utf-8")
    md_stem = task_md.stem   # "task-1-mysql"

    click.echo(f"\n[prepare-inputs] source : {task_md}")
    click.echo(f"[prepare-inputs] level  : {proficiency}")

    # ── 1. Resolve stack names ────────────────────────────────────────────────
    names: list[str] = list(stack)
    if not names:
        names = _detect_stacks(md_content)
        if not names:
            raise click.ClickException(
                "Could not auto-detect a tech stack from the markdown.\n"
                "Provide --stack explicitly, e.g.  --stack MySQL"
            )
        click.echo(f"[prepare-inputs] stack  : {names}  (auto-detected)")
    else:
        click.echo(f"[prepare-inputs] stack  : {names}")

    # ── 2. Fetch competencies from Supabase ───────────────────────────────────
    click.echo(f"[prepare-inputs] querying Supabase ({env}) for competencies...")
    supabase = init_supabase(env)
    competency_data: list[dict] = []
    for name in names:
        rows = fetch_competencies_from_db(supabase, name, proficiency)
        click.echo(f"  '{name}' ({proficiency}) -> {len(rows)} row(s)")
        for row in rows:
            competency_data.append({
                "competency_id": row["competency_id"],
                "created_at":    row["created_at"],
                "proficiency":   row["proficiency"],
                "organization_id": row["organization_id"],
                "name":          row["name"],
                "scope":         row["scope"],
                "long_scope":    row.get("long_scope", ""),
            })

    # ── 3. Resolve role_context ───────────────────────────────────────────────
    role_context = _extract_role_description(md_content)
    if role_context:
        click.echo("[prepare-inputs] role_context extracted from '## Role Description' section")
    else:
        click.echo("[prepare-inputs] no Role Description -- generating role_context via LLM...")
        try:
            combined_name = " & ".join(c["name"] for c in competency_data)
            combined_scope = "\n\n---\n\n".join(
                f"[{c['name']}]\n{c.get('long_scope') or c.get('scope', '')}"
                for c in competency_data
            )
            yoe = PROFICIENCY_YOE_MAP.get(proficiency, "1-2")
            openai_client = init_openai_client()
            role_context, _ = generate_role_context(
                openai_client, combined_scope, combined_name, proficiency, yoe, role_description=None,
            )
            click.echo(f"  {role_context[:100]}...")
        except Exception as exc:
            click.echo(f"  WARNING: LLM call failed ({exc}). Using fallback role_context.")
            combined_name = " & ".join(c["name"] for c in competency_data)
            role_context = (
                f"A candidate with {PROFICIENCY_YOE_MAP.get(proficiency, '1-2')} years of "
                f"experience in {combined_name} is expected to complete this assessment at "
                f"the {proficiency} proficiency level."
            )

    # ── 4. Assemble JSON payloads ─────────────────────────────────────────────
    yoe = PROFICIENCY_YOE_MAP.get(proficiency, "1-2")

    background_data = {
        "organization":     HARDCODED_ORGANIZATION,
        "role_context":     role_context,
        "questions_prompt": md_content,
        "yoe":              yoe,
    }

    # ── 5. Resolve output paths ───────────────────────────────────────────────
    out_dir = _output_dir(names, level, md_stem)
    tech_slug  = sanitize_folder_name("_".join(n.lower() for n in names))
    tech_short = tech_slug.replace("input_", "", 1)

    comp_filename = f"competency_{tech_short}_{level}_Utkrusht.json"
    bg_filename   = f"background_forQuestions_utkrusht_{tech_short}_{level}.json"
    comp_path     = out_dir / comp_filename
    bg_path       = out_dir / bg_filename

    click.echo(f"\n[prepare-inputs] output dir : {out_dir}")
    click.echo(f"  competency : {comp_filename}")
    click.echo(f"  background : {bg_filename}")

    # ── 6. Dry-run preview ────────────────────────────────────────────────────
    if dry_run:
        click.echo("\n--- DRY RUN -- no files written ---")
        click.echo("\nCompetency JSON (first 600 chars):")
        click.echo(json.dumps(competency_data, indent=2)[:600])
        click.echo("\nBackground JSON (questions_prompt truncated to 300 chars):")
        preview = {
            **background_data,
            "questions_prompt": background_data["questions_prompt"][:300] + "...[truncated]",
        }
        click.echo(json.dumps(preview, indent=2))
        return

    # ── 7. Write files ────────────────────────────────────────────────────────
    out_dir.mkdir(parents=True, exist_ok=True)
    comp_written = write_json_safe(comp_path, competency_data, force)
    bg_written   = write_json_safe(bg_path, background_data, force)

    if not (comp_written or bg_written):
        click.echo("\nNo files written (all already exist). Use --force to overwrite.")
        return

    click.echo("\n[prepare-inputs] files written successfully.")


if __name__ == "__main__":
    main()
