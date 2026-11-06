from __future__ import annotations

import threading

from PySide6.QtCore import QThread

from xmluvation.domain.errors import Cancelled, ValidationError
from xmluvation.presentation.tasks import TaskRunner


def test_success_is_delivered_on_gui_thread(qtbot, runner: TaskRunner) -> None:
    gui_thread = QThread.currentThread()
    seen: dict[str, object] = {}

    def work(ctx):
        seen["worker"] = threading.current_thread().name
        ctx.message("hello")
        ctx.progress(1, 1, "done")
        return 42

    def on_success(value):
        seen["value"] = value
        seen["gui"] = QThread.currentThread() is gui_thread

    finished = []
    runner.start(
        work,
        on_success=on_success,
        on_message=lambda m: seen.setdefault("message", m),
        on_progress=lambda d, t, s: seen.setdefault("progress", (d, t, s)),
        on_finished=lambda: finished.append(True),
    )
    qtbot.waitUntil(lambda: bool(finished), timeout=5000)
    assert seen["value"] == 42 and seen["gui"] is True
    assert seen["message"] == "hello" and seen["progress"] == (1, 1, "done")
    assert seen["worker"] != threading.main_thread().name
    assert runner.active_count == 0


def test_failure_and_finished_callbacks(qtbot, runner: TaskRunner) -> None:
    errors: list[BaseException] = []
    finished = []

    def work(_ctx):
        raise ValidationError("bad input")

    runner.start(work, on_error=errors.append, on_finished=lambda: finished.append(True))
    qtbot.waitUntil(lambda: bool(finished), timeout=5000)
    assert isinstance(errors[0], ValidationError)


def test_cancellation(qtbot, runner: TaskRunner) -> None:
    started = threading.Event()
    cancelled = []

    def work(ctx):
        started.set()
        while True:
            ctx.token.raise_if_cancelled()

    handle = runner.start(work, on_cancelled=lambda: cancelled.append(True))
    assert started.wait(5)
    handle.cancel()
    qtbot.waitUntil(lambda: bool(cancelled), timeout=5000)
    assert not handle.running


def test_shutdown_cancels_running_tasks(qtbot) -> None:
    runner = TaskRunner()
    started = threading.Event()

    def work(ctx):
        started.set()
        while not ctx.token.cancelled:
            pass
        raise Cancelled()

    runner.start(work)
    assert started.wait(5)
    assert runner.shutdown(5000) is True
