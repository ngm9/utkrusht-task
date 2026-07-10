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


# ─────────────────────────────────────────────────────────────────────
# LLM route decider + inline auto-apply (fit-existing path).
#
# ``draft_remediation`` above is the deterministic, draft-only fallback.
# ``route_or_draft`` below is the smart path the pipeline calls first: an
# LLM reads EVERY built template's capability sheet and decides whether the
# missing capability fits an EXISTING template (e.g. utkrusht-infra's DinD
# can host a broker as a task docker-compose container) or genuinely needs a
# new image. On ``fit_existing`` it applies the capability patch + re-points
# this combo's match INLINE and returns a resolved plan so generation can
# proceed. On ``new_template`` (or any failure) it falls back to the
# human-facing rebuild draft and returns None — the caller then hard-aborts
# with a clear reason (the deliberate backstop).
# ─────────────────────────────────────────────────────────────────────

_ROUTE_SYSTEM_PROMPT = """You decide how to close a runtime-template gap for a \
technical assessment task.

A classifier could not match a competency combo to any built E2B template. \
Your job is to decide, from the EXISTING built templates below, whether the \
missing capabilities can be hosted by one of them WITHOUT rebuilding an image, \
or whether a brand-new template must be authored.

EXISTING TEMPLATES:
{templates_block}

DECISION RULES:
- fit_existing: an existing template already has the SUBSTRATE to run the \
missing capability without an image rebuild. The ONLY qualifying substrate is \
Docker-in-Docker: the target MUST have "docker-ce"/"docker"/"docker-ce-cli" in \
its tools, so a datastore/broker/service (postgres, redis, kafka, pulsar, \
rabbitmq, ...) runs as a task-shipped docker-compose container — no baked \
install needed. Do NOT pick a template that lacks Docker in its tools, and do \
NOT pick a language-specific template (e.g. go-base, node-base) just because a \
persona sounds related — those pin a runtime and will mismatch the task. For a \
datastore/broker/service capability, STRONGLY PREFER the runtime-agnostic infra \
template (primary_runtime "infra") when one has Docker. Pick the best \
target_template_id, ONE persona from that template's personas, and a \
capability_patch: a JSON object mapping capability list-keys (e.g. "frameworks", \
"datastores", "protocols", "tags") to the array of canonical values to ADD, so \
the classifier matches this need next time.
- new_template: NO existing template can host it without baking real install \
steps into a base image (no DinD substrate, or a first-class language SDK is \
required). In that case set target_template_id and capability_patch to null.

OUTPUT: ONLY a JSON object, no prose, no markdown fences, EXACTLY these fields:
  • decision: "fit_existing" OR "new_template"
  • target_template_id: string (a built template id) OR null
  • persona: string (one of the chosen template's personas) OR null
  • capability_patch: object mapping capability-key -> array of strings, OR null
  • rationale: one short sentence
"""


def _render_route_templates_block(active) -> str:
    """Format active TemplateSpec list as capability sheets for the decider."""
    if not active:
        return "  (no built templates — every decision must be new_template)"
    lines = []
    for t in active:
        caps = t.capabilities or {}
        lines.append(f"\n- template_id: {t.template_id}")
        lines.append(f"  primary_runtime: {t.primary_runtime}")
        lines.append(f"  personas: {t.personas}")
        lines.append(f"  tools: {caps.get('tools') or []}")
        lines.append(f"  datastores: {caps.get('datastores') or []}")
        lines.append(f"  frameworks: {caps.get('frameworks') or []}")
        lines.append(f"  tags: {caps.get('tags') or []}")
    return "\n".join(lines)


def _extract_json_obj(text: str) -> dict:
    """First balanced top-level JSON object in text."""
    start = text.find("{")
    if start == -1:
        raise ValueError("no JSON object in decider reply")
    depth = 0
    for i in range(start, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                return json.loads(text[start:i + 1])
    raise ValueError("unbalanced braces in decider reply")


def _decide_route_llm(missing_capabilities: list[str], active) -> dict:
    """Ask the Claude-role LLM to route the gap. Returns the parsed decision
    dict. Raises on transport/parse failure (caller treats as new_template)."""
    from infra.llm_provider import make_llm_client, resolve_model
    from infra.prompt_cache import cache_messages

    client = make_llm_client()
    system = _ROUTE_SYSTEM_PROMPT.format(
        templates_block=_render_route_templates_block(active)
    )
    user = (
        "The task needs these missing capabilities: "
        f"{missing_capabilities}. Decide fit_existing vs new_template."
    )
    resp = client.chat.completions.create(
        model=resolve_model("classifier"),
        messages=cache_messages([
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ]),
    )
    raw = resp.choices[0].message.content or ""
    return _extract_json_obj(raw)


def _apply_capability_patch(supabase, template_id: str, patch: dict) -> int:
    """Merge ``patch`` (key -> list) into the template's capabilities, bump
    registry_version, invalidate that template's match cache. Returns the new
    registry_version. Raises if the template row is absent.
    """
    row = (supabase.table("templates").select("capabilities, registry_version")
           .eq("template_id", template_id).limit(1).execute())
    rows = row.data or []
    if not rows:
        raise RuntimeError(
            f"route: target template {template_id!r} not found in templates table"
        )
    caps = dict(rows[0].get("capabilities") or {})
    for key, values in (patch or {}).items():
        if not isinstance(values, list):
            continue
        existing = list(caps.get(key) or [])
        caps[key] = existing + [v for v in values if v not in existing]
    next_version = int(rows[0].get("registry_version") or 1) + 1
    supabase.table("templates").update({
        "capabilities": caps,
        "registry_version": next_version,
    }).eq("template_id", template_id).execute()

    from infra.e2b.template_builder import _invalidate_match_cache
    _invalidate_match_cache(supabase, template_id)
    return next_version


def route_or_draft(match, combo_key: str, task_shape: str | None, *, supabase=None):
    """Smart resolution of a no-match infra gap.

    On ``fit_existing``: apply the capability patch to the target template,
    re-point THIS combo's match row at it, and return a fully-resolved
    ``ResolvedPlan`` (with the target template hydrated) so generation can
    proceed on THIS run. On ``new_template`` or ANY failure: fall back to the
    human-facing rebuild draft (``draft_remediation``) and return ``None`` —
    the caller then hard-aborts with a clear reason.

    Never raises — a raise here would defeat the point (the caller's hard stop
    is the intended backstop, not a stack trace).
    """
    # Only actionable for an INFRA no-match that carries missing capabilities.
    if (task_shape or "").strip().lower() != "infra":
        return None
    if match is None or match.template_id is not None or not match.missing_capabilities:
        return None

    try:
        from flows.tech.stages.generate.runtime_resolver import (
            ResolvedPlan,
            _build_supabase_client,
            _get_template,
            _load_active_templates,
            _match_write,
        )
        from infra.classifier.runtime import TaskTemplateMatch

        client = supabase or _build_supabase_client()
        active = _load_active_templates(client)

        decision = _decide_route_llm(list(match.missing_capabilities), active)
        route = (decision.get("decision") or "").strip().lower()
        target_id = decision.get("target_template_id")
        rationale = decision.get("rationale") or ""

        if route != "fit_existing" or not target_id:
            logger.info(
                f"route: combo={combo_key!r} decided new_template "
                f"(target={target_id!r}) — {rationale} — drafting rebuild scaffold"
            )
            draft_remediation(match, combo_key, supabase=client)
            return None

        active_by_id = {t.template_id: t for t in active}
        target = active_by_id.get(target_id)
        if target is None:
            logger.warning(
                f"route: decider picked unknown target {target_id!r} — "
                "falling back to rebuild draft"
            )
            draft_remediation(match, combo_key, supabase=client)
            return None

        # DETERMINISTIC GUARD 1: a fit_existing target is only legitimate if it
        # actually has the Docker-in-Docker substrate to host the service as a
        # task container. Reject → rebuild draft.
        target_tools = list((target.capabilities or {}).get("tools") or [])
        if not any(t in _DOCKER_TOOL_NAMES for t in target_tools):
            logger.warning(
                f"route: decider picked {target_id!r} but it has no "
                f"Docker-in-Docker in tools — not a real fit; drafting rebuild"
            )
            draft_remediation(match, combo_key, supabase=client)
            return None

        # DETERMINISTIC GUARD 2: nearly every template has DinD, so the LLM can
        # wrongly pick a LANGUAGE-specific template (go-base, node-base) whose
        # primary_runtime then mismatches the task (the go-base misfire). For a
        # DinD-hosted external service the correct home is the runtime-AGNOSTIC
        # infra template. If the decider picked a language template but a built
        # infra template exists, override to infra so the runtime stays neutral.
        if target.primary_runtime != "infra":
            infra_target = next(
                (t for t in active
                 if t.primary_runtime == "infra"
                 and any(x in _DOCKER_TOOL_NAMES
                         for x in ((t.capabilities or {}).get("tools") or []))),
                None,
            )
            if infra_target is not None:
                logger.info(
                    f"route: overriding decider pick {target_id!r} "
                    f"(runtime={target.primary_runtime!r}) -> "
                    f"{infra_target.template_id!r} (runtime-agnostic infra host)"
                )
                target = infra_target
                target_id = infra_target.template_id

        # Persona must be one the target actually declares.
        persona = decision.get("persona")
        if persona not in (target.personas or []):
            persona = (target.personas or [None])[0]

        patch = decision.get("capability_patch") or {}
        new_version = _apply_capability_patch(client, target_id, patch)

        # Re-point THIS combo's match at the now-capable target so this run —
        # and every future run — resolves it. Persist an audit draft too.
        new_match = TaskTemplateMatch(
            template_id=target_id,
            persona=persona,
            confidence=match.confidence,
            no_match_reason=None,
            missing_capabilities=[],
            suggested_template=None,
        )
        _match_write(client, combo_key, new_match, registry_version=new_version)

        try:
            _write_draft(RemediationDraft(
                combo_key=combo_key,
                missing_capabilities=list(match.missing_capabilities),
                suggested_template=target_id,
                strategy="declarative",
                rationale=f"[auto-applied inline] {rationale}",
                capability_patch=patch,
                status="approved",
                approved_at=_now_iso(),
            ))
        except Exception:  # noqa: BLE001 — audit draft is best-effort
            pass

        template = _get_template(client, target_id)
        logger.info(
            f"route: combo={combo_key!r} FIT_EXISTING -> {target_id!r} "
            f"persona={persona!r} patch={patch} — applied inline; gate will run"
        )
        return ResolvedPlan(combo_key=combo_key, match=new_match, template=template)
    except Exception as exc:  # noqa: BLE001 — backstop is the caller's hard stop
        logger.warning(
            f"route: combo={combo_key!r} routing failed: {exc} — "
            "falling back to hard-abort"
        )
        try:
            draft_remediation(match, combo_key)
        except Exception:  # noqa: BLE001
            pass
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
