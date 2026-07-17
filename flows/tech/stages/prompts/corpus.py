"""Durable prompt corpus — Supabase-backed reference prompts.

Generated prompts are written to ``data/generated/agent_prompts/`` on the
container's disposable writable layer, and the retriever only reads the curated
``task_generation_prompts/`` tree. So a generated prompt is lost on the next
redeploy AND could never become a reference anyway — novel stacks fall to the
Level-6 generic skeleton on every run, forever.

This module is the durable store + the valve between the two trees:

* :func:`save_candidate`  — after a prompt is generated (status ``candidate``).
* :func:`approve_for_task` — when the task built from it shipped (``approved``).
* :func:`approved_root`    — materialise approved rows to a dir the retriever globs.

The curated/generated split guards against model collapse (agent output training
on agent output). We keep that guard and gate promotion on a signal we already
compute: the task passed the E2B gate + evals and reached ``status='ready'``.
An unproven prompt never becomes a reference; a bad one is revoked with one
UPDATE back to ``candidate``.

Every function is best-effort — a corpus failure must never fail a task
generation. Callers get a bool / an empty path, never an exception.
"""
from __future__ import annotations

import logging
import re
import tempfile
from functools import lru_cache
from pathlib import Path

from infra.supabase import init_supabase

logger = logging.getLogger(__name__)

TABLE = "task_prompts"

# Mirrors retriever.LEVEL_FOLDERS. Imported lazily inside functions instead of at
# module scope — retriever imports this module, so a top-level import would cycle.


def slug_for(competency_names: list[str], proficiency: str) -> str:
    """Build the corpus slug: ``["Python","SQL"], BASIC -> python_sql_basic_prompt``.

    The single source of truth for prompt naming — ``__main__._expected_path``
    builds the on-disk filename from this too. The retriever matches references
    by FILENAME tokens, so a materialised approved prompt only resolves like a
    curated one if the row key and the filename are built identically.
    """
    parts = []
    for name in competency_names:
        s = name.lower()
        s = re.sub(r"\.js\b", "js", s)
        s = re.sub(r"\s*[-/&]\s*", "_", s)
        s = re.sub(r"[\s.]+", "_", s)
        s = re.sub(r"[^a-z0-9_]", "", s)
        s = re.sub(r"_+", "_", s).strip("_")
        parts.append(s)
    return f"{'_'.join(parts)}_{proficiency.lower()}_prompt"


def save_candidate(
    competency_names: list[str],
    proficiency: str,
    source: str,
    *,
    env: str = "dev",
) -> bool:
    """Upsert a freshly generated prompt as an unproven ``candidate``.

    Upsert (not insert) on ``slug`` so regenerating a combo replaces its row
    rather than accumulating duplicates the materialiser would have to dedupe.
    Re-generating deliberately resets an ``approved`` row to ``candidate``: the
    source changed, so the prior proof no longer applies to it.
    """
    slug = slug_for(competency_names, proficiency)
    try:
        init_supabase(env).table(TABLE).upsert(
            {
                "slug": slug,
                "level": proficiency.upper(),
                "competencies": list(competency_names),
                "source": source,
                "status": "candidate",
                "task_id": None,
                "updated_at": "now()",
            },
            on_conflict="slug",
        ).execute()
        logger.info("Saved prompt candidate %s to corpus", slug)
        return True
    except Exception as exc:  # noqa: BLE001 — never fail a generation over the corpus
        logger.warning("Could not save prompt candidate %s: %s", slug, exc)
        return False


def approve_for_task(
    competencies: list[dict],
    task_id: str,
    *,
    env: str = "dev",
) -> bool:
    """Promote the prompt behind a shipped task to ``approved``.

    Called once a task reaches ``status='ready'`` — i.e. it passed the E2B gate
    and the evals and its GitHub artifacts exist. That is the quality signal that
    earns a prompt reference status.

    ``competencies`` is the task's ``criterias`` list (``{name, proficiency}``),
    which is what the call site already has in scope.
    """
    names = [c.get("name") for c in competencies if c.get("name")]
    if not names:
        return False
    proficiency = (competencies[0].get("proficiency") or "").upper()
    if not proficiency:
        return False

    slug = slug_for(names, proficiency)
    try:
        res = (
            init_supabase(env)
            .table(TABLE)
            .update({"status": "approved", "task_id": task_id, "updated_at": "now()"})
            .eq("slug", slug)
            .execute()
        )
        if not res.data:
            # No row: the prompt pre-dates the corpus, or came from the curated
            # tree (which needs no promotion). Not an error.
            logger.info("No corpus row for %s — nothing to promote", slug)
            return False
        logger.info("Promoted prompt %s to approved (task %s)", slug, task_id)
        return True
    except Exception as exc:  # noqa: BLE001
        logger.warning("Could not promote prompt %s: %s", slug, exc)
        return False


@lru_cache(maxsize=4)
def approved_root(env: str = "dev") -> Path | None:
    """Materialise ``approved`` prompts into ``<tmp>/<Level>/<slug>/<slug>.py``.

    Returns the root dir for the retriever to glob alongside the curated tree, or
    ``None`` when there's nothing approved / the fetch failed (retrieval then
    behaves exactly as it does today).

    Cached per env: this runs once per process, on the first retrieval. A prompt
    approved mid-process isn't picked up until the next run — acceptable, since
    approval happens at the END of a generation and the next run is a fresh
    subprocess anyway.

    # ponytail: whole-corpus fetch + tmpdir materialise. Fine at this size
    # (hundreds of rows, ~50KB each). If the corpus outgrows memory, filter the
    # query by level and cache the dir on a volume instead.
    """
    from flows.tech.stages.prompts.retriever import LEVEL_FOLDERS

    try:
        rows = (
            init_supabase(env)
            .table(TABLE)
            .select("slug,level,source")
            .eq("status", "approved")
            .execute()
        ).data or []
    except Exception as exc:  # noqa: BLE001
        logger.warning("Could not load approved prompt corpus: %s", exc)
        return None

    if not rows:
        return None

    root = Path(tempfile.mkdtemp(prefix="prompt-corpus-"))
    written = 0
    for row in rows:
        folder = LEVEL_FOLDERS.get((row.get("level") or "").upper())
        slug = row.get("slug")
        source = row.get("source")
        if not (folder and slug and source):
            continue
        # <Level>/<slug>/<slug>.py — the canonical per-slug layout _list_prompt_files
        # treats as curated.
        dest = root / folder / slug / f"{slug}.py"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(source, encoding="utf-8")
        written += 1

    logger.info("Materialised %d approved prompts to %s", written, root)
    return root if written else None
