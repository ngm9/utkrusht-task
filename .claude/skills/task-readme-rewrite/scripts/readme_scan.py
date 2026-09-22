#!/usr/bin/env python3
"""Scan task READMEs in Supabase for answer-leak patterns.

Read-only. Heuristic. Errs toward flagging — read the README before acting.

    python readme_scan.py --env dev
    python readme_scan.py --env prod --enabled-only
    python readme_scan.py --env prod --task-id <UUID> --show
    python readme_scan.py --env dev --json
"""
import argparse
import ast
import json
import os
import re
import sys
import urllib.parse
import urllib.request

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))


def load_env(path):
    out = {}
    try:
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                out[k.strip()] = v.strip().strip('"').strip("'")
    except FileNotFoundError:
        pass
    return out


def supabase(env_name):
    env = load_env(os.path.join(ROOT, ".env"))
    suffix = "APTITUDETESTSDEV" if env_name == "dev" else "APTITUDETESTS"
    url, key = env.get(f"SUPABASE_URL_{suffix}"), env.get(f"SUPABASE_API_KEY_{suffix}")
    if not url or not key:
        sys.exit(f"missing SUPABASE_URL_{suffix} / SUPABASE_API_KEY_{suffix} in .env")
    return url.rstrip("/"), key


def fetch(url, key, params):
    q = urllib.parse.urlencode(params, safe="*,.()=>")
    req = urllib.request.Request(f"{url}/rest/v1/tasks?{q}",
                                 headers={"apikey": key, "Authorization": f"Bearer {key}"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


# ---------- README parsing ----------

SECTION_ALIASES = {
    "task overview": "overview", "overview": "overview",
    "objectives": "objectives",
    "helpful tips": "tips", "tips": "tips", "hints": "tips",
    "how to verify": "verify", "verification": "verify",
    "application access": "access",
}


def parse_readme(raw):
    """Return (sections dict, structure_notes). Accepts markdown or dict-repr."""
    notes = []
    if raw is None:
        return {}, ["readme_content is NULL"]
    if isinstance(raw, dict):
        d = raw
    elif isinstance(raw, str) and raw.lstrip().startswith("{"):
        try:
            d = ast.literal_eval(raw)
            notes.append("readme_content stored as Python dict repr, not markdown")
        except Exception:
            d = None
    else:
        d = None
    if isinstance(d, dict):
        secs = {}
        for k, v in d.items():
            key = SECTION_ALIASES.get(k.replace("_", " ").lower(), k)
            secs[key] = v if isinstance(v, list) else [str(v)]
        return secs, notes

    text = str(raw)
    secs, cur = {}, None
    heading_levels = set()
    for line in text.splitlines():
        m = re.match(r"^(#{1,6})\s+(.*?)\s*$", line)
        if m:
            heading_levels.add(len(m.group(1)))
            cur = SECTION_ALIASES.get(m.group(2).strip().lower(), m.group(2).strip().lower())
            secs.setdefault(cur, [])
            continue
        if cur is None:
            continue
        s = line.strip()
        if not s:
            continue
        s = re.sub(r"^[-*•]\s+", "", s)
        secs[cur].append(s)
    if heading_levels and heading_levels != {2}:
        notes.append(f"headings use level(s) {sorted(heading_levels)}, expected ## only")
    if not secs:
        notes.append("no ## sections found")
    order = [k for k in secs if k in ("overview", "objectives", "tips", "access", "verify")]
    want = [k for k in ("overview", "objectives", "tips", "access", "verify") if k in order]
    if order != want:
        notes.append(f"section order {order}, expected {want}")
    return secs, notes


# ---------- leak heuristics ----------

DEFECT_ENUM = re.compile(
    r"\b(but|however|currently|intentionally|the current)\b[^.]{0,160}"
    r"\b(duplicat|slow|too much|too many|larger than|fragile|not (clearly )?defined|"
    r"limited|missing|unreliabl|incorrect|broken|leak|cycling|stall|fails?|does not|"
    r"incomplete|inconsistent|unhealthy)\b", re.I)
FIX_VERB = re.compile(
    r"^(ensure|align|make|keep|improve|reduce|minimi[sz]e|establish|preserve|enable|apply|"
    r"add|configure|implement|use|set|introduce|replace|refactor|optimi[sz]e|harden|fix|"
    r"restrict|limit|isolate|persist|cache)\b", re.I)
MECHANISM = re.compile(
    r"\b(visibility timeout|dead[- ]letter|dlq|redrive|idempotent\w*|idempotenc\w*|partial[- ]batch|"
    r"batch item failure|retry|retries|broadcast|partition(ed|ing)?|shuffle|udf|append|overwrite|"
    r"multi-?stage|staged build|base image|image layer|build cache|copy order|\.dockerignore|"
    r"healthcheck|health check|start_period|depends_on|restart polic|resource (limit|boundar)|"
    r"mem_limit|named volume|tmpfs|read-only|non-root|root user|capabilit|"
    r"seccomp|log rotation|log driver|max-size|correlation id|"
    r"stable identifier|identifier[s]? (should|that) remain|delivery timing|execution window|"
    r"maximum runtime|conditional (put|write)|upsert|connection pool|n\+1|"
    r"eager loading|lazy loading|row[- ]level lock|optimistic lock|pessimistic lock)\b", re.I)
PATHY = re.compile(r"(`[^`]*[/.][^`]*`|\b[\w-]+\.(py|sh|tf|yml|yaml|json|java|go|js|ts|toml|xml)\b|\b[\w-]+/[\w./-]+)")
COMMANDY = re.compile(r"(`[^`]+`|https?://\S+|localhost:\d+|\bdocker(-compose)?\b|\bcurl\b|\bkubectl\b|\bawslocal\b|\bspark-submit\b|\bnpm\b|\bmvn\b|\bpytest\b)", re.I)
REPRO = re.compile(r"\b(resend|replay|re-?run(ning)?|send (the same|a mixed)|using the .* fixture|fixtures?/)\b", re.I)
AFTER_FIX = re.compile(r"^after (your|the) fix", re.I)

# Design/build shape, inferred from the task title. A Verify section written as pass
# conditions is CORRECT on a repair task (knowing the symptom is not knowing the cause)
# but a leak on a design/build task, where the pass condition IS the spec the Objectives
# deliberately withheld. Gated on the title so repair tasks are not flagged en masse.
DESIGN_SHAPE = re.compile(r"\b(design|build|rework|create|implement|harden)\b|^make\b", re.I)
PASS_CONDITION = re.compile(
    r"\bshould\s+(?:\w+\s+){0,2}"
    r"(result in|carry|produce|leave|rebuild|contain|match|exist|be\b|never\b|only\b|still\b)",
    re.I)
CANDIDATE_DIRECTED = re.compile(
    r"^(you (should|must|need to|will)|the candidate (should|must|will|needs to)|"
    r"implement|build (the|a)|add (a|an)|write (a|the)|ensure you|make sure you|"
    r"diagnose|investigate|inspect|update (the|code)|fix (the|it)|repair|"
    r"harden (the|it)|restore|review (the|it)|analy[sz]e|optimi[sz]e (the|it))\b", re.I)
CANDIDATE_DIRECTED_ANYWHERE = re.compile(
    r"\bthe candidate (should|must|will|needs to|investigates|improves|updates|"
    r"then (updates|improves|edits|fixes|writes|adds))\b", re.I)
EVAL_CRITERIA = re.compile(
    r"\b(what separates|separates a strong|whether\b.{0,80}\bwhether|"
    r"is (judged|graded|evaluated) on|we (look|evaluate) for|reasoning behind|"
    r"quality of (the|your) (design|reasoning|decisions))\b", re.I)

# Concrete build/runtime artifacts. A short_overview bullet[1] that names two or more of
# these is almost always enumerating the RULES rather than stating the OUTCOME — the
# altitude failure. The DESIGN_REVIEW reference overviews name none of them.
ARTIFACT_NOUN = re.compile(
    r"\b(commit|sha|branch|main line|mainline|tag|tags|tagged|image|images|container|"
    r"replica|partition|queue|topic|endpoint|index|cache|credential|secret|token|"
    r"webhook|cron|volume|registry)\b", re.I)

OBS_OPENER = re.compile(r"^(the |a |an )?([\w-]+ (team|engineer|reviewer|developer|analyst|operator|customer)s?|finance|qa|ops|operations|security|platform|on-call)\b", re.I)

# The THIRD leak (2026-09-15): a goal statement that ENUMERATES the instances the candidate
# is meant to discover ("invalid date or lifecycle choices", "money, status, and deletion
# semantics", "trial, site, date, amendment, and manifest"). Three or more comma-separated
# short nouns, or an "X or Y choices/semantics/context" pair, in one bullet. The fix is
# always "keep the verb, name the class" — see SKILL.md.
ENUM_INSTANCES = re.compile(
    r"\b(\w+(?:\s\w+)?,\s+\w+(?:\s\w+)?,\s+(?:and|or)\s+\w+(?:\s\w+)?)\b"
    r"|\b(\w+ or \w+ (choices|semantics|context|values|fields|rules|paths))\b", re.I)
# Concrete identifiers / dates in an objective are always an instance.
INSTANCE_ID = re.compile(r"\b([A-Z]{2,}-\d{2,}|\d{4}-\d{2}-\d{2}|[a-z]+_v\d+(\.\d+)?|v\d+\.\d+)\b")

# Objectives the generator pastes verbatim from a prompt module's "good style examples",
# and the approved per-task sets. A README whose objectives match a set that belongs to a
# DIFFERENT task is the "same task in a different costume" failure (3976d75a vs 6a49454c).
KNOWN_OBJECTIVE_SETS = {
    "rag-module-examples": [
        "keep generated answers grounded in eligible evidence.",
        "preserve evidence provenance across the answer lifecycle.",
        "make evaluation failures separable and reproducible.",
        "what other risks should the quality gate surface before rollout?",
    ],
    "6a49454c oncology": [
        "keep answers consistent with the rules that apply.",
        "make every answer auditable back to what it was built from.",
        "make evaluation failures separable and reproducible.",
        "surface whatever else the quality gate should catch before rollout.",
    ],
    "3976d75a fintech-graph": [
        "keep answers whole when the facts live in different places.",
        "make every answer distinguishable from a close match.",
        "make disagreements in the bank's own records visible, never silently resolved.",
        "surface whatever else should change when the product history changes.",
    ],
}
# A design/build Verify probe that tells the candidate what the REPORT must contain.
REPORT_SHAPE = re.compile(r"\b(dimensions?|separate (metrics|scores)|per-dimension|reproducibility key|run id)\b", re.I)


def q(s, n=70):
    s = s.strip()
    return f'("{s[:n]}…")' if len(s) > n else f'("{s}")'


def scan_sections(secs, title=None, task_id=None):
    hard, soft = [], []
    # Repair vs design/build. Several checks below encode the REPAIR house style
    # (team-framed objectives, no paths). On a design/build task those are the
    # wrong standard, so they are gated off rather than firing as false positives.
    is_design = bool(title and DESIGN_SHAPE.search(title))

    ov = " ".join(secs.get("overview", []))
    if ov:
        m = DEFECT_ENUM.search(ov)
        if m:
            # Design/build overviews legitimately say "something exists but is not
            # trusted / does not cover it" without naming a single defect. Only flag
            # when the match actually names one.
            generic = re.search(r"\b(trust|cover|exist)\w*\b", m.group(0), re.I) and \
                not re.search(r"\b(duplicat|slow|too much|too many|larger than|leak|"
                              r"stall|fragile|incorrect|broken|unhealthy)\w*\b", m.group(0), re.I)
            if is_design and generic:
                pass
            else:
                hard.append("overview: enumerates defects " + q(m.group(0)))
        if re.search(r"\bintentionally\b", ov, re.I):
            hard.append("overview: says setup is 'intentionally' broken/incomplete")
        if len(ov) > 1200:
            soft.append(f"overview: long ({len(ov)} chars)")

    objs = secs.get("objectives", [])
    if not objs:
        soft.append("objectives: missing")
    for o in objs:
        if FIX_VERB.match(o):
            if MECHANISM.search(o):
                hard.append("objectives: names fix " + q(o)); break
            if not is_design:
                # Imperative is the CORRECT voice for design/build objectives.
                soft.append("objectives: imperative outcome, not observation " + q(o)); break
    for o in objs:
        if MECHANISM.search(o):
            hard.append("objectives: mechanism " + q(MECHANISM.search(o).group(0))); break
    for o in objs:
        if PATHY.search(o):
            hard.append("objectives: file/path " + q(PATHY.search(o).group(0))); break
    for o in objs:
        if REPRO.search(o):
            soft.append("objectives: reproduction recipe " + q(REPRO.search(o).group(0))); break
    if objs and not is_design and not any(OBS_OPENER.match(o) for o in objs):
        soft.append("objectives: not observation-style (no team/role opener)")
    if objs and is_design:
        # Inverted for design/build: team framing forces the bullet to state the rule.
        framed = [o for o in objs if OBS_OPENER.match(o)]
        if framed:
            soft.append("objectives: team-framed on a design/build task " + q(framed[0])
                        + " — observation framing forces the rule into the bullet; use a plain goal statement")
        because = [o for o in objs if re.search(r",\s*because\b", o, re.I)]
        if because:
            soft.append("objectives: 'because' clause " + q(because[0])
                        + " — the justification is a second hint; the goal alone is enough")
    # Third leak: enumerated instances. Hard on design/build (ADVANCED is strict);
    # soft on repair, where one instance-level observation is sometimes the symptom.
    for o in objs:
        m = ENUM_INSTANCES.search(o) or INSTANCE_ID.search(o)
        if m:
            msg = "objectives: enumerates instances " + q(m.group(0)) + " — name the class, not the members"
            (hard if is_design else soft).append(msg); break
    # Pasted / shared objective sets. Exact match on 3+ of a known set's lines.
    norm = [re.sub(r"\s+", " ", o.strip().lower()) for o in objs]
    for label, known in KNOWN_OBJECTIVE_SETS.items():
        if task_id and label.startswith(task_id[:8]):
            continue  # this IS the task the set was approved for
        overlap = sum(1 for o in norm if o in known)
        if overlap >= 3:
            if label.endswith("examples"):
                hard.append(f"objectives: {overlap}/{len(known)} bullets are the prompt module's example objectives pasted verbatim ({label})")
            else:
                soft.append(f"objectives: {overlap}/{len(known)} bullets identical to the approved set of another task ({label}) — objectives must be distinct per task unless this IS that task")
            break
    longest = max((len(o) for o in objs), default=0)
    if longest > 260:
        soft.append(f"objectives: longest bullet {longest} chars")
    if len(objs) > 8:
        soft.append(f"objectives: {len(objs)} bullets")

    tips = secs.get("tips", [])
    for t in tips:
        if MECHANISM.search(t):
            hard.append("tips: mechanism " + q(MECHANISM.search(t).group(0))); break
    pathy_tips = [t for t in tips if PATHY.search(t)]
    # A design/build task may name ONE shipped script whose invocation is part of the
    # design; more than one path is still a leak.
    if pathy_tips and not (is_design and len(pathy_tips) == 1):
        soft.append("tips: file/path " + q(PATHY.search(pathy_tips[0]).group(0)))
    for t in tips:
        if REPRO.search(t):
            soft.append("tips: scenario hint " + q(REPRO.search(t).group(0))); break
    for t in tips:
        if re.search(r"\b(grading|graded|the grader|assessed|assessment|scored?)\b", t, re.I):
            soft.append("tips: mentions grading " + q(t)
                        + " — tips are working advice, not a description of the assessment"); break
    for t in tips:
        if re.search(r"\b(on |at )?port \d{2,5}\b|localhost:\d+|https?://", t, re.I):
            soft.append("tips: access/setup detail " + q(t)
                        + " — the platform already surfaces ports/links via expected_ports and the tour"); break
    if len(tips) > 6:
        soft.append(f"tips: {len(tips)} bullets")

    acc = secs.get("access", [])
    for a in acc:
        if re.search(r"\b(pay attention to|understand whether|to understand|use docker .* to)\b", a, re.I):
            soft.append("access: coaching paragraph " + q(a)); break

    ver = secs.get("verify", [])
    if not ver:
        soft.append("verify: missing")
    for v in ver:
        if MECHANISM.search(v):
            hard.append("verify: mechanism " + q(MECHANISM.search(v).group(0))); break
    for v in ver:
        if re.search(r"\b(configuration|config|settings?)\b", v, re.I) and COMMANDY.search(v):
            hard.append("verify: config/command " + q(v)); break
    cmds = [v for v in ver if COMMANDY.search(v) and not re.search(r"\b(tests?|invariants?|verify)/", v)]
    if len(cmds) >= 2:
        soft.append(f"verify: {len(cmds)} bullets carry commands/URLs")
    if sum(1 for v in ver if AFTER_FIX.match(v)) >= 3:
        soft.append("verify: repetitive 'After your fix' openers")
    if is_design:
        for v in secs.get("verify", []):
            if REPORT_SHAPE.search(v):
                hard.append("verify: probe describes the report's shape " + q(REPORT_SHAPE.search(v).group(0))
                            + " — say what outcome to judge, not what the report must contain"); break
    if title and DESIGN_SHAPE.search(title):
        assertive = [v for v in ver if PASS_CONDITION.search(v)]
        if len(assertive) >= 2:
            soft.append(
                f"verify: {len(assertive)} bullets state pass conditions "
                + q(assertive[0])
                + " — reads like a design/build task, where the pass condition is the spec "
                  "the objectives withheld; use probe style instead")

    return hard, soft


def scan_overview(bullets):
    """Score task_blob.short_overview (the 'Problem Statement' card) — a different
    field from the README, with its own 3-bullet framing rules. Returns (hard, soft)."""
    hard, soft = [], []
    if not isinstance(bullets, list) or len(bullets) != 3:
        soft.append(f"short_overview: {len(bullets) if isinstance(bullets, list) else 0} bullets, expected 3")
        return hard, soft
    b0, b1, b2 = bullets
    if CANDIDATE_DIRECTED.match(b1.strip()) or CANDIDATE_DIRECTED_ANYWHERE.search(b1):
        hard.append("short_overview: bullet[1] instructs the candidate directly " + q(b1) +
                    " — should state what the system must guarantee, not what to build")
    if MECHANISM.search(b1):
        hard.append("short_overview: bullet[1] mechanism " + q(MECHANISM.search(b1).group(0)))
    if not EVAL_CRITERIA.search(b2):
        soft.append("short_overview: bullet[2] doesn't read as evaluation criteria " + q(b2))
    # Altitude: bullet[1] should state outcomes, not the rules that achieve them. The
    # voice check above passes a correctly-phrased bullet that still lists every
    # requirement — that is the failure this catches.
    arts = sorted({a.lower() for a in ARTIFACT_NOUN.findall(b1)})
    if len(arts) >= 2:
        soft.append("short_overview: bullet[1] names concrete artifacts (" + ", ".join(arts)
                    + ") — reads as an enumeration of the rules; bullet 2 states outcomes, "
                      "not the rules that achieve them")
    return hard, soft


def verdict(hard, soft, notes):
    if hard:
        return "rewrite"
    if soft or notes:
        return "review"
    return "clean"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--env", choices=["dev", "prod"], default="dev")
    ap.add_argument("--task-id")
    ap.add_argument("--enabled-only", action="store_true")
    ap.add_argument("--show", action="store_true", help="print the README after the report")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--all-statuses", action="store_true", help="include non-ready rows")
    ap.add_argument("--check-overview", action="store_true",
                    help="also scan task_blob.short_overview (the Problem Statement card) for framing")
    args = ap.parse_args()

    url, key = supabase(args.env)
    params = {"select": "task_id,is_enabled,status,readme_content,task_blob,created_at",
              "order": "created_at.desc"}
    if args.task_id:
        params["task_id"] = f"eq.{args.task_id}"
    else:
        if not args.all_statuses:
            params["status"] = "eq.ready"
        if args.enabled_only:
            params["is_enabled"] = "eq.true"
    rows = fetch(url, key, params)
    if isinstance(rows, dict):
        sys.exit(f"supabase error: {rows}")

    results = []
    for r in rows:
        blob = r.get("task_blob") or {}
        if isinstance(blob, str):
            try:
                blob = json.loads(blob)
            except Exception:
                blob = {}
        secs, notes = parse_readme(r.get("readme_content"))
        hard, soft = scan_sections(secs, title=blob.get("title"), task_id=r["task_id"])
        if args.check_overview:
            ov_hard, ov_soft = scan_overview(blob.get("short_overview"))
            hard, soft = hard + ov_hard, soft + ov_soft
        results.append({
            "task_id": r["task_id"], "enabled": r.get("is_enabled"), "status": r.get("status"),
            "title": blob.get("title"), "repo": (blob.get("resources") or {}).get("github_repo"),
            "verdict": verdict(hard, soft, notes), "hard": hard, "soft": soft, "structure": notes,
            "readme": r.get("readme_content"), "short_overview": blob.get("short_overview"),
        })

    if args.json:
        for x in results:
            x.pop("readme", None)
        print(json.dumps(results, indent=2, default=str))
        return

    order = {"rewrite": 0, "review": 1, "clean": 2}
    results.sort(key=lambda x: (order[x["verdict"]], not x["enabled"]))
    counts = {k: sum(1 for x in results if x["verdict"] == k) for k in order}
    print(f"env={args.env}  tasks={len(results)}  rewrite={counts['rewrite']}  review={counts['review']}  clean={counts['clean']}\n")
    for x in results:
        flag = "on " if x["enabled"] else "off"
        print(f"{x['task_id'][:8]}  {flag}  {x['verdict']:<7}  {x['title'] or '(no title)'}")
        for h in x["hard"]:
            print(f"    ! {h}")
        for s in x["soft"]:
            print(f"    - {s}")
        for n in x["structure"]:
            print(f"    ~ {n}")
        if args.show:
            print("\n" + "-" * 78)
            print(x["readme"])
            if args.check_overview:
                print("--- short_overview ---")
                for b in (x.get("short_overview") or []):
                    print(" -", b)
            print("-" * 78 + "\n")


if __name__ == "__main__":
    main()
