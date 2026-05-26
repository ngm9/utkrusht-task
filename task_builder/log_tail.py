"""Live tailing of a pipeline stage's stdout/stderr log files.

While a stage runs, `_run_stage` streams its subprocess output into
`<label>.stdout` / `<label>.stderr` files under `.task_agent_runs`. A
``StageLogTailer`` watches those files on a background thread and forwards
newly-appended content to a callback so the UI can show it live.
"""
from __future__ import annotations

import threading
import time
from pathlib import Path
from typing import Callable

# Callback receiving each decoded chunk of newly-appended log text.
EmitChunk = Callable[[str], None]

_DEFAULT_INTERVAL_S = 0.5


class StageLogTailer:
    """Polls a set of log files for appended content on a daemon thread.

    Usage:
        tailer = StageLogTailer([stdout_path, stderr_path], emit)
        tailer.start()   # before the stage subprocess runs
        ...               # stage runs, writing to the files
        tailer.stop()    # after it finishes — performs one final flush read

    A file that does not exist yet is simply skipped until it appears, so the
    tailer may be started before `_run_stage` opens the files.
    """

    def __init__(self, paths: list[Path], emit: EmitChunk, *,
                 interval_s: float = _DEFAULT_INTERVAL_S) -> None:
        self._paths = list(paths)
        self._emit = emit
        self._interval_s = interval_s
        self._offsets: dict[Path, int] = {p: 0 for p in self._paths}
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        """Begin tailing on a background daemon thread."""
        if self._thread is not None:
            raise RuntimeError("StageLogTailer already started")
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """Stop tailing and join the thread (which does one final flush read)."""
        self._stop.set()
        if self._thread is not None:
            self._thread.join()
            self._thread = None

    def _run(self) -> None:
        # `Event.wait` returns True the moment stop() is called, so the loop
        # exits promptly; the trailing _drain() flushes any final bytes.
        while not self._stop.wait(self._interval_s):
            self._drain()
        self._drain()

    def _drain(self) -> None:
        """Emit newly-appended content from every tailed file."""
        for path in self._paths:
            chunk = self._read_new(path)
            if chunk:
                self._emit(chunk)

    def _read_new(self, path: Path) -> str:
        """Return text appended to `path` since the last read, decoded.

        Returns an empty string if the file does not exist yet or nothing new
        was written. Reading is byte-oriented so a chunk boundary may fall mid
        line — harmless, since chunks are concatenated downstream.
        """
        try:
            with path.open("rb") as fh:
                fh.seek(self._offsets[path])
                data = fh.read()
        except FileNotFoundError:
            return ""
        self._offsets[path] += len(data)
        return data.decode("utf-8", errors="replace")
