"""Template remediation — draft a fix when ``resolve_plan`` finds no template.

Today, when the LLM classifier can't match a competency combo to any built
template, ``require_infra_template`` (runtime_resolver.py) hard-aborts task
generation. That abort is deliberate and stays — it's the fix for a real
prior incident (RabbitMQ shipped classified-infra with no working template,
the gate silently skipped, and an undeployable task went out).

What's missing is everything BEFORE that abort: the classifier's `no_match`
already carries a `suggested_template` + `missing_capabilities`, but nothing
in the pipeline reads them. This module closes that gap — best-effort, and
NEVER in place of the hard-abort: it queues an actionable, human-reviewable
draft describing how the gap could be closed, and a separate `approve()`
step (run deliberately, never automatically) is what actually changes
anything live.

Two remediation strategies:

  DECLARATIVE — the suggested template already has Docker-in-Docker
    ("docker-ce" in its `tools`). Every existing datastore on
    ``utkrusht-infra`` (postgres/mysql/mongo/redis/elasticsearch) works this
    same way already: NONE of them are baked into the base image — they're
    reachable because the task ships its own docker-compose.yml and the
    template can run it. This was proven live for LocalStack on a CDK task.
    So adding a missing capability here means: add it to `datastores`/`tags`
    — no image rebuild required, because the underlying mechanism (DinD)
    already exists and already works.

  REBUILD — the suggested template has no Docker-in-Docker, or no template
    matched at all. Closing this gap means real install steps baked into
    the base image, which this module deliberately does NOT auto-author or
    auto-build. It drafts a scaffold + rationale for a human engineer to
    fill in and build via the existing `template.py` / `build_dev.py` flow.

``approve()`` only ever executes the DECLARATIVE path automatically — it is
a metadata-only Supabase update (capabilities + cache invalidation), never a
real E2B build. The REBUILD path always requires a human to author and run
the real build themselves; `approve()` refuses to touch it.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from infra.logger_config import logger

_QUEUE_DIR = Path(".task_agent_runs/template_remediation")
_DOCKER_TOOL_NAMES = {"docker-ce", "docker", "docker-ce-cli"}


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _slug(combo_key: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", combo_key.lower()).strip("-")
    return s or "combo"


@dataclass
class RemediationDraft:
    combo_key: str
    missing_capabilities: list[str]
    suggested_template: str | None
    strategy: str  # "declarative" | "rebuild"
    rationale: str
    capability_patch: dict | None = None      # DECLARATIVE: what to merge into the templates row
    rebuild_scaffold: str | None = None       # REBUILD: human-facing TODO scaffold, not executable
    status: str = "pending"                   # pending | approved | rejected
    created_at: str = field(default_factory=_now_iso)
    approved_at: str | None = None

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2)

    @classmethod
    def from_dict(cls, d: dict) -> "RemediationDraft":
        return cls(**d)


def _queue_path(combo_key: str) -> Path:
    return _QUEUE_DIR / f"{_slug(combo_key)}.json"


def _write_draft(draft: RemediationDraft) -> Path:
    _QUEUE_DIR.mkdir(parents=True, exist_ok=True)
    path = _queue_path(draft.combo_key)
    path.write_text(draft.to_json(), encoding="utf-8")
    return path


def draft_remediation(match, combo_key: str, supabase=None) -> RemediationDraft | None:
    """Best-effort: draft a remediation for a no-match combo and queue it.

    Returns None (never raises) when there's nothing actionable to draft —
    e.g. the classifier gave no ``suggested_template``/``missing_capabilities``
    at all. Callers should treat this as informational; it must never affect
    whether ``require_infra_template`` still aborts the current run.
    """
    try:
        if match is None or not match.missing_capabilities or not match.suggested_template:
            return None

        target_tools: list[str] = []
        target_capabilities: dict = {}
        if supabase is not None:
            try:
                from flows.tech.stages.generate.runtime_resolver import _get_template
                spec = _get_template(supabase, match.suggested_template)
                if spec is not None:
                    target_capabilities = spec.capabilities or {}
                    target_tools = list(target_capabilities.get("tools") or [])
            except Exception as exc:  # noqa: BLE001
                logger.warning(
                    f"template_remediation: could not hydrate {match.suggested_template!r} "
                    f"to check for Docker-in-Docker: {exc}"
                )

        has_dind = any(t in _DOCKER_TOOL_NAMES for t in target_tools)

        if has_dind:
            existing_datastores = list(target_capabilities.get("datastores") or [])
            existing_tags = list(target_capabilities.get("tags") or [])
            new_datastores = existing_datastores + [
                c for c in match.missing_capabilities if c not in existing_datastores
            ]
            new_tags = existing_tags + [
                c for c in match.missing_capabilities if c not in existing_tags
            ]
            draft = RemediationDraft(
                combo_key=combo_key,
                missing_capabilities=list(match.missing_capabilities),
                suggested_template=match.suggested_template,
                strategy="declarative",
                rationale=(
                    f"{match.suggested_template!r} already has Docker-in-Docker "
                    f"({sorted(t for t in target_tools if t in _DOCKER_TOOL_NAMES)}). "
                    f"Every existing datastore on this template "
                    f"({existing_datastores or 'none declared'}) already works this same "
                    f"way — none are baked into the base image; tasks ship their own "
                    f"docker-compose.yml and this template runs it (proven live for "
                    f"LocalStack on a CDK task). Adding {match.missing_capabilities} the "
                    f"same way needs no image rebuild — only a capability declaration, so "
                    f"future tasks are told this is available and how (docker-compose in "
                    f"the task repo, not a pre-running service)."
                ),
                capability_patch={"datastores": new_datastores, "tags": new_tags},
            )
        else:
            draft = RemediationDraft(
                combo_key=combo_key,
                missing_capabilities=list(match.missing_capabilities),
                suggested_template=match.suggested_template,
                strategy="rebuild",
                rationale=(
                    f"{match.suggested_template!r} has no Docker-in-Docker in its "
                    f"declared tools, so {match.missing_capabilities} can't be added the "
                    f"low-risk docker-compose way. This needs real install steps baked "
                    f"into the base image — a human must author and build this; "
                    f"template_remediation will not do so automatically."
                ),
                rebuild_scaffold=(
                    f"# TODO(human): add real install steps for {match.missing_capabilities}\n"
                    f"# to infra/e2b/templates/{match.suggested_template}/template.py\n"
                    f"# (or author a brand-new infra/e2b/templates/<new-id>/template.py)\n"
                    f"# then: cd infra/e2b/templates/<id> && python build_dev.py\n"
                    f"#       (verify) && python build_prod.py\n"
                ),
            )

        path = _write_draft(draft)
        logger.info(
            f"template_remediation: queued {draft.strategy!r} draft for "
            f"combo={combo_key!r} -> {path}"
        )
        return draft
    except Exception as exc:  # noqa: BLE001 — best-effort, must never break the abort path
        logger.warning(f"template_remediation: draft failed for {combo_key!r}: {exc}")
        return None


def list_pending() -> list[RemediationDraft]:
    if not _QUEUE_DIR.exists():
        return []
    drafts = []
    for path in sorted(_QUEUE_DIR.glob("*.json")):
        try:
            drafts.append(RemediationDraft.from_dict(json.loads(path.read_text())))
        except Exception as exc:  # noqa: BLE001
            logger.warning(f"template_remediation: could not load {path}: {exc}")
    return drafts


def show(slug: str) -> RemediationDraft | None:
    path = _QUEUE_DIR / f"{slug}.json"
    if not path.exists():
        return None
    return RemediationDraft.from_dict(json.loads(path.read_text()))


def approve(slug: str, supabase=None) -> RemediationDraft:
    """Apply a DECLARATIVE draft for real (Supabase capability patch + cache
    invalidation). REBUILD drafts are refused — those always need a human to
    author and build the real template themselves; this function will not
    do it for them.
    """
    path = _QUEUE_DIR / f"{slug}.json"
    if not path.exists():
        raise FileNotFoundError(f"no pending draft for {slug!r} at {path}")
    draft = RemediationDraft.from_dict(json.loads(path.read_text()))

    if draft.strategy != "declarative":
        raise ValueError(
            f"draft {slug!r} is strategy={draft.strategy!r} — only 'declarative' drafts "
            f"can be auto-applied. 'rebuild' drafts require a human to author real "
            f"install steps and build the template themselves (see rebuild_scaffold)."
        )
    if draft.status == "approved":
        logger.info(f"template_remediation: {slug!r} already approved — no-op")
        return draft

    if supabase is None:
        from flows.tech.stages.generate.runtime_resolver import _build_supabase_client
        supabase = _build_supabase_client()

    row = (supabase.table("templates").select("capabilities, registry_version")
           .eq("template_id", draft.suggested_template).limit(1).execute())
    rows = row.data or []
    if not rows:
        raise RuntimeError(
            f"template_remediation: {draft.suggested_template!r} not found in "
            f"Supabase templates table — cannot apply capability patch."
        )
    # Merge-only: replace exactly the two patched keys, keep every other key
    # (language_versions/frameworks/protocols/tools/requires/...) untouched.
    current_capabilities = dict(rows[0].get("capabilities") or {})
    current_capabilities["datastores"] = draft.capability_patch["datastores"]
    current_capabilities["tags"] = draft.capability_patch["tags"]
    next_registry_version = int(rows[0].get("registry_version") or 1) + 1

    supabase.table("templates").update({
        "capabilities": current_capabilities,
        "registry_version": next_registry_version,
    }).eq("template_id", draft.suggested_template).execute()

    from infra.e2b.template_builder import _invalidate_match_cache
    _invalidate_match_cache(supabase, draft.suggested_template)

    draft.status = "approved"
    draft.approved_at = _now_iso()
    _write_draft(draft)
    logger.info(f"template_remediation: approved + applied {slug!r}")
    return draft


def _cli() -> int:
    p = argparse.ArgumentParser(description="template remediation queue")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list")
    s = sub.add_parser("show"); s.add_argument("slug")
    a = sub.add_parser("approve"); a.add_argument("slug")
    args = p.parse_args()

    if args.cmd == "list":
        drafts = list_pending()
        if not drafts:
            print("(no pending drafts)")
        for d in drafts:
            print(f"{_slug(d.combo_key):40s} {d.strategy:12s} {d.status:10s} "
                  f"missing={d.missing_capabilities} suggested={d.suggested_template}")
        return 0
    if args.cmd == "show":
        d = show(args.slug)
        if d is None:
            print(f"no draft found for {args.slug!r}", file=sys.stderr)
            return 1
        print(d.to_json())
        return 0
    if args.cmd == "approve":
        d = approve(args.slug)
        print(f"approved: {d.to_json()}")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(_cli())
