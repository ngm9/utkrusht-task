"""End-to-end smoke for per-stage S3 log upload + DB persistence.

Synthesizes a fake PipelineResult with three stages, each pointing at a
real local log file, runs the same worker codepath that production does,
verifies the DB row, then cleans up both the row and the S3 objects.

Run with `.env` sourced and PYTHONPATH=. — costs nothing in LLM tokens,
performs 3 small S3 PUTs against the dev bucket and one Postgres round trip.
"""
from __future__ import annotations

import os
import tempfile
import uuid
from pathlib import Path

import boto3

from apps.orchestrator.pipeline import PipelineResult, StageResult
from generators.task.persistence import init_supabase
from infra.jobs import repository as jobs_repo
from infra.jobs.worker import _upload_stage_logs


def main() -> None:
    sb = init_supabase("dev")

    job_id = str(uuid.uuid4())
    workspace = Path(tempfile.mkdtemp(prefix="stage_smoke_"))
    print(f"job_id={job_id}")
    print(f"workspace={workspace}")

    # 1. Fake three stage log files on disk.
    stages: list[StageResult] = []
    for label in ("00_preflight", "01_input_files", "02_scenarios"):
        log_path = workspace / f"{label}.log"
        log_path.write_text(
            f"stage {label} smoke output\n" + ("filler line\n" * 20),
            encoding="utf-8",
        )
        stages.append(StageResult(
            label=label, status="ok", duration_s=0.5, log_path=log_path,
        ))

    # 2. Insert a minimal generation_jobs row so the FK + RLS path works.
    sb.table("generation_jobs").insert({
        "id": job_id,
        "brief": {"smoke": True, "competency_names": ["smoke"]},
        "env": "dev",
        "status": "queued",
    }).execute()

    # 3. Run the actual worker codepath.
    result = PipelineResult(job_id=job_id, status="ok", workspace=workspace)
    result.stages = stages
    urls = _upload_stage_logs(job_id, "dev", result)
    print(f"uploaded {len(urls)} stages:")
    for label, url in urls.items():
        print(f"  {label} -> {url}")

    # 4. Persist via the new repo helper.
    jobs_repo.update_stage_log_urls(job_id, urls, env="dev")

    # 5. Re-read to confirm round trip.
    row = (
        sb.table("generation_jobs")
        .select("id, stage_log_urls")
        .eq("id", job_id)
        .single()
        .execute()
    ).data
    persisted = (row or {}).get("stage_log_urls") or {}
    print(f"DB.stage_log_urls keys: {sorted(persisted.keys())}")
    assert persisted == urls, "round-trip mismatch"
    print("OK round-trip matches")

    # 6. Cleanup — delete the row and the S3 objects.
    sb.table("generation_jobs").delete().eq("id", job_id).execute()
    s3 = boto3.client("s3", region_name=os.environ["S3_REGION"])
    for label in urls:
        s3.delete_object(
            Bucket="aptitudetestsdev",
            Key=f"task_builder/{job_id}/{label}.log",
        )
    print("cleanup complete")


if __name__ == "__main__":
    main()
