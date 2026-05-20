"""StageLogTailer — live tailing of a stage's stdout/stderr log files."""
import time

from task_builder.log_tail import StageLogTailer


def test_tailer_emits_appended_content(tmp_path):
    """Content appended while the tailer runs is emitted."""
    log = tmp_path / "stage.stderr"
    log.write_text("")
    chunks: list[str] = []

    tailer = StageLogTailer([log], chunks.append, interval_s=0.01)
    tailer.start()
    with log.open("a", encoding="utf-8") as fh:
        fh.write("line one\nline two\n")
        fh.flush()
    time.sleep(0.05)
    tailer.stop()

    assert "".join(chunks) == "line one\nline two\n"


def test_tailer_flushes_remaining_content_on_stop(tmp_path):
    """stop() performs a final read, even when written within one interval."""
    log = tmp_path / "stage.stdout"
    log.write_text("")
    chunks: list[str] = []

    # A long interval guarantees the periodic poll never fires before stop().
    tailer = StageLogTailer([log], chunks.append, interval_s=10)
    tailer.start()
    log.write_text("late content")
    tailer.stop()

    assert "".join(chunks) == "late content"


def test_tailer_tolerates_missing_file(tmp_path):
    """A path that never appears yields no chunks and no error."""
    chunks: list[str] = []

    tailer = StageLogTailer([tmp_path / "never.stderr"], chunks.append,
                            interval_s=0.01)
    tailer.start()
    time.sleep(0.03)
    tailer.stop()

    assert chunks == []


def test_tailer_merges_two_files(tmp_path):
    """Both stdout and stderr are tailed into one stream."""
    out = tmp_path / "stage.stdout"
    err = tmp_path / "stage.stderr"
    out.write_text("")
    err.write_text("")
    chunks: list[str] = []

    tailer = StageLogTailer([out, err], chunks.append, interval_s=10)
    tailer.start()
    out.write_text("from stdout")
    err.write_text("from stderr")
    tailer.stop()

    joined = "".join(chunks)
    assert "from stdout" in joined
    assert "from stderr" in joined


def test_tailer_does_not_re_emit_old_content(tmp_path):
    """Each byte is emitted exactly once across multiple poll cycles."""
    log = tmp_path / "stage.stderr"
    log.write_text("")
    chunks: list[str] = []

    tailer = StageLogTailer([log], chunks.append, interval_s=0.01)
    tailer.start()
    with log.open("a", encoding="utf-8") as fh:
        fh.write("first\n")
        fh.flush()
        time.sleep(0.05)
        fh.write("second\n")
        fh.flush()
    time.sleep(0.05)
    tailer.stop()

    assert "".join(chunks) == "first\nsecond\n"
