"""Regression: when scenarios_prepared=True but the input files are gone
(container disk wiped on redeploy), the generate run must regenerate them
(00_preflight + 01_input_files) instead of failing at stage 03."""
import task_builder.runner as r
from task_builder.slots import TaskBrief


def test_prepared_regenerates_when_input_files_missing(monkeypatch, tmp_path):
    calls = []

    def fake_stage_runner(combo_dir, emit):
        def _stage(label, cmd):
            calls.append(label)
            return {"exit_code": 0, "stdout": str(tmp_path / f"{label}.stdout")}
        return _stage

    comp, bg = tmp_path / "c.json", tmp_path / "b.json"
    locate_calls = {"n": 0}

    def fake_locate(names, level, since):
        locate_calls["n"] += 1
        if locate_calls["n"] == 1:  # first call = the "prepared" shortcut → files gone
            raise FileNotFoundError("wiped")
        return comp, bg

    monkeypatch.setattr(r, "_make_stage_runner", fake_stage_runner)
    monkeypatch.setattr(r, "_pick_python", lambda: "python")
    monkeypatch.setattr(r, "_locate_input_files", fake_locate)
    monkeypatch.setattr(r, "_summarise_task_stage", lambda p: "PASSED")
    monkeypatch.setattr(r, "_extract_task_result", lambda p: {
        "task_id": "t", "task_url": "u", "task_name": "n",
        "task_type": "ty", "competencies": "c",
    })

    events = []
    brief = TaskBrief(competencies=["Golang", "PostgreSQL"], proficiency="INTERMEDIATE",
                      role="Backend", domain="e-commerce", focus_areas=["x"])
    r.run_generate_for_brief(brief, run_id="t", emit=events.append,
                             runs_root=tmp_path, scenarios_prepared=True)

    # fell back to regenerating input files, then completed
    assert "00_preflight" in calls and "01_input_files" in calls
    assert "02_scenarios" not in calls  # pool reused, not regenerated
    assert events[-1].status == "completed"
