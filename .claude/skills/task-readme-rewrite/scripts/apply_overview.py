#!/usr/bin/env python3
"""Apply a fixed short_overview (the 'Problem Statement' card, task_blob.short_overview)
to one task, correctly and safely.

Exists because hand-writing the fetch -> merge -> PATCH inline every time is exactly how
a real bug shipped once already: sending the raw task_blob dict as the PATCH body instead
of wrapping it as {"task_blob": {...}} makes PostgREST try to set columns named after the
blob's own keys. This script is the one place that does the write correctly, self-checks
the draft against scan_overview() before touching anything, verifies the write landed by
re-reading the row, and re-scans afterward so "clean" is confirmed, not assumed.

Never writes without the self-check passing first. --dry-run does everything except the
PATCH, so a bad draft is caught before Supabase is touched.

Usage:
    # bullets from a JSON file: {"task_id": [...three strings...]} or just [...]
    python apply_overview.py --task-id <uuid> --env prod --bullets-file bullets.json
    python apply_overview.py --task-id <uuid> --env prod --bullets-file bullets.json --also-env dev
    python apply_overview.py --task-id <uuid> --env prod --bullets-file bullets.json --dry-run

    # bullets inline (one --bullet per line, in order)
    python apply_overview.py --task-id <uuid> --env prod \\
        --bullet "..." --bullet "..." --bullet "..."
"""
import argparse
import importlib.util
import json
import os
import sys
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("readme_scan", os.path.join(HERE, "readme_scan.py"))
rs = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(rs)


def req(method, url, key, body=None):
    data = json.dumps(body).encode() if body is not None else None
    r = urllib.request.Request(url, data=data, method=method, headers={
        "apikey": key, "Authorization": f"Bearer {key}", "Content-Type": "application/json",
        "Prefer": "return=representation"})
    try:
        with urllib.request.urlopen(r) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        sys.exit(f"HTTP {e.code} from {method} {url}: {e.read().decode()}")


def load_bullets(args):
    if args.bullet:
        bullets = args.bullet
    elif args.bullets_file:
        data = json.load(open(args.bullets_file))
        if isinstance(data, dict):
            if args.task_id in data:
                bullets = data[args.task_id]
            elif len(data) == 1:
                bullets = next(iter(data.values()))
            else:
                sys.exit(f"--bullets-file has multiple keys and none match --task-id {args.task_id}; "
                         f"keys: {list(data.keys())}")
        elif isinstance(data, list):
            bullets = data
        else:
            sys.exit("--bullets-file must contain a JSON list of 3 strings, or a {task_id: [...]} object")
    else:
        sys.exit("pass either --bullets-file or three --bullet flags")
    if not isinstance(bullets, list) or len(bullets) != 3:
        sys.exit(f"expected exactly 3 bullets, got {len(bullets) if isinstance(bullets, list) else type(bullets)}")
    for i, b in enumerate(bullets):
        if not isinstance(b, str) or not b.strip():
            sys.exit(f"bullet[{i}] is empty or not a string")
    return bullets


def apply_one(env_name, task_id, bullets, dry_run):
    url, key = rs.supabase(env_name)
    rows = req("GET", f"{url}/rest/v1/tasks?select=task_id,task_blob&task_id=eq.{task_id}", key)
    if not rows:
        print(f"[{env_name}] {task_id}: NOT FOUND, skipping")
        return False
    blob = rows[0]["task_blob"]
    if isinstance(blob, str):
        blob = json.loads(blob)
    before = blob.get("short_overview")
    blob = dict(blob)
    blob["short_overview"] = bullets

    if dry_run:
        print(f"[{env_name}] {task_id}: DRY RUN — would replace short_overview")
        print("  before:", json.dumps(before))
        print("  after: ", json.dumps(bullets))
        return True

    out = req("PATCH", f"{url}/rest/v1/tasks?task_id=eq.{task_id}", key, {"task_blob": blob})
    if not out:
        sys.exit(f"[{env_name}] {task_id}: PATCH returned no rows — nothing was written")
    written = out[0]["task_blob"].get("short_overview")
    if written != bullets:
        sys.exit(f"[{env_name}] {task_id}: write verification FAILED — what landed does not match "
                  f"what was sent.\n  sent:    {json.dumps(bullets)}\n  landed:  {json.dumps(written)}")
    print(f"[{env_name}] {task_id}: written and verified ({len(bullets)} bullets)")
    return True


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--task-id", required=True)
    ap.add_argument("--env", choices=["dev", "prod"], default="prod")
    ap.add_argument("--also-env", choices=["dev", "prod"], help="apply the same fix to a second env too")
    ap.add_argument("--bullets-file")
    ap.add_argument("--bullet", action="append", help="repeat 3 times, in order, as an inline alternative to --bullets-file")
    ap.add_argument("--dry-run", action="store_true", help="validate and show the diff, write nothing")
    ap.add_argument("--skip-self-check", action="store_true",
                    help="DANGEROUS: push even if scan_overview() flags the draft. Never use without a reason.")
    args = ap.parse_args()

    bullets = load_bullets(args)

    hard, soft = rs.scan_overview(bullets)
    if hard or soft:
        print("scan_overview() flags on this draft:")
        for h in hard:
            print("  !", h)
        for s in soft:
            print("  -", s)
    if hard and not args.skip_self_check:
        sys.exit("refusing to push a draft with hard flags — fix the bullets or pass --skip-self-check "
                  "(not recommended) if you are certain the flag is a false positive.")
    if not hard and not soft:
        print("scan_overview(): clean, no flags")

    envs = [args.env] + ([args.also_env] if args.also_env and args.also_env != args.env else [])
    ok = True
    for env_name in envs:
        ok = apply_one(env_name, args.task_id, bullets, args.dry_run) and ok

    if not args.dry_run and ok:
        for env_name in envs:
            print(f"\n--- re-scanning [{env_name}] to confirm ---")
            os.system(f'{sys.executable} "{os.path.join(HERE, "readme_scan.py")}" '
                      f'--env {env_name} --task-id {args.task_id} --check-overview')


if __name__ == "__main__":
    main()
