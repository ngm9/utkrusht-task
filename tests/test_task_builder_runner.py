"""Background pipeline runner — stage events and failure handling."""
from unittest.mock import patch

from task_builder.runner import run_pipeline_for_brief, StageEvent
from task_builder.slots import TaskBrief


def _brief():
    return TaskBrief(competencies=["Java"], proficiency="BASIC", role="Eng",
                     focus_areas=["idempotency"], domain="fintech")


def _stage_ok(label):
    return {"label": label, "exit_code": 0,
            "stdout": "/tmp/x.stdout", "stderr": "/tmp/x.stderr", "cmd": []}


def test_runner_emits_one_event_per_stage_on_success(tmp_path):
    events: list[StageEvent] = []

    with patch("task_builder.runner._run_stage", side_effect=lambda d, label, c: _stage_ok(label)), \
         patch("task_builder.runner._locate_input_files",
               return_value=(tmp_path / "c.json", tmp_path / "b.json")), \
         patch("task_builder.runner._summarise_task_stage", return_value="TASK CREATED"):
        run_pipeline_for_brief(_brief(), run_id="r1", emit=events.append,
                               runs_root=tmp_path)

    labels = [e.stage for e in events if e.status in ("ok", "failed")]
    assert labels == ["00_preflight", "01_input_files", "02_scenarios",
                      "03_prompt", "04_tasks"]
    assert events[-1].stage == "done"
    assert events[-1].status == "completed"


def test_runner_stops_and_reports_on_stage_failure(tmp_path):
    events: list[StageEvent] = []

    def fake_stage(d, label, c):
        rec = _stage_ok(label)
        if label == "02_scenarios":
            rec["exit_code"] = 1
        return rec

    with patch("task_builder.runner._run_stage", side_effect=fake_stage), \
         patch("task_builder.runner._locate_input_files",
               return_value=(tmp_path / "c.json", tmp_path / "b.json")):
        run_pipeline_for_brief(_brief(), run_id="r2", emit=events.append,
                               runs_root=tmp_path)

    assert any(e.stage == "02_scenarios" and e.status == "failed" for e in events)
    assert events[-1].stage == "done"
    assert events[-1].status == "failed"
    assert not any(e.stage == "03_prompt" for e in events)  # stopped early


def test_extract_task_result_parses_id_and_url(tmp_path):
    from task_builder.runner import _extract_task_result
    stdout = tmp_path / "s.out"
    stdout.write_text(" Task ID: abc-123\n Task Name: x\n"
                      " GitHub Repository: https://github.com/org/repo\n")
    result = _extract_task_result(stdout)
    assert result["task_id"] == "abc-123"
    assert result["task_url"] == "https://github.com/org/repo"
    assert result["task_name"] == "x"


def test_extract_task_result_missing_file_returns_none(tmp_path):
    from task_builder.runner import _extract_task_result
    result = _extract_task_result(tmp_path / "nope.out")
    assert result["task_id"] is None
    assert result["task_url"] is None
    assert result["task_name"] is None
    assert result["task_type"] is None
    assert result["competencies"] is None


def test_extract_task_result_parses_full_success_block(tmp_path):
    from task_builder.runner import _extract_task_result
    stdout = tmp_path / "s.out"
    stdout.write_text(
        " Task Creation Successful!\n"
        " Task Type: BUILD\n"
        " Task ID: 11111111-2222-3333-4444-555555555555\n"
        " Task Name: Idempotent payment webhook\n"
        " Competencies Covered: Java, Spring Boot\n"
        " GitHub Repository: https://github.com/org/task-repo\n"
        " TASK CREATION COMPLETED SUCCESSFULLY!\n"
    )
    result = _extract_task_result(stdout)
    assert result["task_id"] == "11111111-2222-3333-4444-555555555555"
    assert result["task_name"] == "Idempotent payment webhook"
    assert result["task_type"] == "BUILD"
    assert result["competencies"] == "Java, Spring Boot"
    assert result["task_url"] == "https://github.com/org/task-repo"


def test_extract_task_result_missing_lines_yield_none(tmp_path):
    from task_builder.runner import _extract_task_result
    stdout = tmp_path / "s.out"
    stdout.write_text(" Task ID: only-an-id\n")
    result = _extract_task_result(stdout)
    assert result["task_id"] == "only-an-id"
    assert result["task_name"] is None
    assert result["task_type"] is None
    assert result["competencies"] is None
    assert result["task_url"] is None


def test_extract_task_result_competencies_covered_not_summary_line(tmp_path):
    """Reads 'Competencies Covered:' and ignores the later bare
    'Competencies:' summary line."""
    from task_builder.runner import _extract_task_result
    stdout = tmp_path / "s.out"
    stdout.write_text(
        " Competencies Covered: Real Value\n"
        " Competencies: Different Summary Value\n"
    )
    result = _extract_task_result(stdout)
    assert result["competencies"] == "Real Value"


def test_done_event_carries_task_fields_and_env(tmp_path):
    """The completed 'done' event surfaces the extracted task fields + env."""
    events: list[StageEvent] = []
    stage4_stdout = tmp_path / "04.out"
    stage4_stdout.write_text(
        " Task ID: tid-9\n Task Name: Demo\n Task Type: BUILD\n"
        " Competencies Covered: Go\n"
        " GitHub Repository: https://github.com/org/r\n"
    )

    def fake_stage(d, label, c):
        rec = _stage_ok(label)
        if label == "04_tasks":
            rec["stdout"] = str(stage4_stdout)
        return rec

    with patch("task_builder.runner._run_stage", side_effect=fake_stage), \
         patch("task_builder.runner._locate_input_files",
               return_value=(tmp_path / "c.json", tmp_path / "b.json")), \
         patch("task_builder.runner._summarise_task_stage", return_value="TASK CREATED"):
        run_pipeline_for_brief(_brief(), run_id="r-fields", emit=events.append,
                               env="prod", runs_root=tmp_path)

    done = events[-1]
    assert done.stage == "done" and done.status == "completed"
    assert done.task_id == "tid-9"
    assert done.task_name == "Demo"
    assert done.task_type == "BUILD"
    assert done.competencies == "Go"
    assert done.task_url == "https://github.com/org/r"
    assert done.env == "prod"


def test_runner_reports_failure_on_unknown_stage4_outcome(tmp_path):
    events = []
    with patch("task_builder.runner._run_stage",
               side_effect=lambda d, label, c: _stage_ok(label)), \
         patch("task_builder.runner._locate_input_files",
               return_value=(tmp_path / "c.json", tmp_path / "b.json")), \
         patch("task_builder.runner._summarise_task_stage",
               return_value="UNKNOWN — inspect stage 4 logs"):
        run_pipeline_for_brief(_brief(), run_id="r3", emit=events.append,
                               runs_root=tmp_path)
    assert events[-1].stage == "done"
    assert events[-1].status == "failed"


def test_runner_threads_env_into_db_stages(tmp_path):
    """The Supabase-touching stages (preflight, input, prompt, tasks) must
    carry the chosen --env."""
    captured: dict[str, list[str]] = {}

    def capture(d, label, cmd):
        captured[label] = cmd
        return _stage_ok(label)

    with patch("task_builder.runner._run_stage", side_effect=capture), \
         patch("task_builder.runner._locate_input_files",
               return_value=(tmp_path / "c.json", tmp_path / "b.json")), \
         patch("task_builder.runner._summarise_task_stage", return_value="TASK CREATED"):
        run_pipeline_for_brief(_brief(), run_id="r-env", emit=lambda e: None,
                               env="prod", runs_root=tmp_path)

    for label in ("00_preflight", "01_input_files", "03_prompt", "04_tasks"):
        cmd = captured[label]
        assert "--env" in cmd, f"{label} missing --env"
        assert cmd[cmd.index("--env") + 1] == "prod", f"{label} wrong --env"


def test_runner_defaults_env_to_dev(tmp_path):
    """Omitting env keeps the prior default (dev) on stage-4 task storage."""
    captured: dict[str, list[str]] = {}

    def capture(d, label, cmd):
        captured[label] = cmd
        return _stage_ok(label)

    with patch("task_builder.runner._run_stage", side_effect=capture), \
         patch("task_builder.runner._locate_input_files",
               return_value=(tmp_path / "c.json", tmp_path / "b.json")), \
         patch("task_builder.runner._summarise_task_stage", return_value="TASK CREATED"):
        run_pipeline_for_brief(_brief(), run_id="r-def", emit=lambda e: None,
                               runs_root=tmp_path)

    cmd = captured["04_tasks"]
    assert cmd[cmd.index("--env") + 1] == "dev"


def test_runner_streams_stage_log_output(tmp_path):
    """Output a stage writes to its log files surfaces as status='log' events,
    ordered before that stage's terminal ok/failed event."""
    events: list[StageEvent] = []

    def fake_stage(combo_dir, label, cmd):
        (combo_dir / f"{label}.stderr").write_text(f"{label}: working\n")
        return _stage_ok(label)

    with patch("task_builder.runner._run_stage", side_effect=fake_stage), \
         patch("task_builder.runner._locate_input_files",
               return_value=(tmp_path / "c.json", tmp_path / "b.json")), \
         patch("task_builder.runner._summarise_task_stage", return_value="TASK CREATED"):
        run_pipeline_for_brief(_brief(), run_id="r-log", emit=events.append,
                               runs_root=tmp_path)

    logs = [e for e in events if e.status == "log"]
    assert any("00_preflight: working" in e.detail for e in logs)

    # The preflight log event must arrive before preflight's "ok" event.
    kinds = [e.status for e in events if e.stage == "00_preflight"]
    assert kinds == ["running", "log", "ok"]
