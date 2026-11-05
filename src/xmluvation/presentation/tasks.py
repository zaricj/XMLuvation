"""Run use cases off the GUI thread and deliver their results on the GUI thread.

Usage::

    runner.start(
        lambda ctx: run_export(spec, ctx, ctx.token),
        on_success=self._export_done,
        on_error=self._report_error,
        on_progress=self._progress,
        on_finished=lambda: self._set_running(False),
    )

The callable receives a :class:`TaskContext`, which is a
:class:`~xmluvation.application.cancellation.ProgressReporter` and carries the task's
cancellation token. All callbacks run on the thread that owns the runner (the GUI
thread), because the worker only emits signals of a QObject living in that thread.
Worker code never touches widgets.
"""

from __future__ import annotations

import itertools
import logging
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from PySide6.QtCore import QObject, QRunnable, QThreadPool, Signal, Slot

from ..application.cancellation import CancellationToken
from ..domain.errors import Cancelled, XMLuvationError

log = logging.getLogger(__name__)

PROGRESS_INTERVAL_S = 0.05


class _Bridge(QObject):
    """Lives in the GUI thread; its signals are emitted from worker threads (queued)."""

    progress = Signal(int, int, int, str)
    message = Signal(int, str)
    succeeded = Signal(int, object)
    failed = Signal(int, object)
    cancelled = Signal(int)


class TaskContext:
    def __init__(self, task_id: int, bridge: _Bridge, token: CancellationToken) -> None:
        self.task_id = task_id
        self.token = token
        self._bridge = bridge
        self._last_progress = 0.0

    def progress(self, done: int, total: int, text: str = "") -> None:
        now = time.monotonic()
        if done >= total or now - self._last_progress >= PROGRESS_INTERVAL_S:
            self._last_progress = now
            self._bridge.progress.emit(self.task_id, done, total, text)

    def message(self, text: str) -> None:
        self._bridge.message.emit(self.task_id, text)


class _Runnable(QRunnable):
    def __init__(self, fn: Callable[[TaskContext], Any], context: TaskContext, bridge: _Bridge):
        super().__init__()
        self.setAutoDelete(True)
        self._fn = fn
        self._context = context
        self._bridge = bridge

    def run(self) -> None:
        task_id = self._context.task_id
        try:
            result = self._fn(self._context)
        except Cancelled:
            self._bridge.cancelled.emit(task_id)
        except XMLuvationError as exc:
            log.info("Task %s failed: %s", task_id, exc)
            self._bridge.failed.emit(task_id, exc)
        except Exception as exc:  # unexpected: keep the traceback in the log
            log.exception("Task %s crashed", task_id)
            self._bridge.failed.emit(task_id, exc)
        else:
            self._bridge.succeeded.emit(task_id, result)


@dataclass
class _Callbacks:
    on_success: Callable[[Any], None] | None = None
    on_error: Callable[[BaseException], None] | None = None
    on_progress: Callable[[int, int, str], None] | None = None
    on_message: Callable[[str], None] | None = None
    on_cancelled: Callable[[], None] | None = None
    on_finished: Callable[[], None] | None = None
    handle: TaskHandle | None = field(default=None, repr=False)


class TaskHandle:
    def __init__(self, task_id: int, token: CancellationToken) -> None:
        self.task_id = task_id
        self.token = token
        self.running = True

    def cancel(self) -> None:
        self.token.cancel()


class TaskRunner(QObject):
    """Owns a thread pool, tracks running tasks, and supports cancellation and shutdown."""

    def __init__(self, parent: QObject | None = None, max_threads: int | None = None) -> None:
        super().__init__(parent)
        self._pool = QThreadPool(self)
        if max_threads:
            self._pool.setMaxThreadCount(max_threads)
        self._bridge = _Bridge(self)
        self._ids = itertools.count(1)
        self._tasks: dict[int, _Callbacks] = {}
        self._bridge.progress.connect(self._on_progress)
        self._bridge.message.connect(self._on_message)
        self._bridge.succeeded.connect(self._on_succeeded)
        self._bridge.failed.connect(self._on_failed)
        self._bridge.cancelled.connect(self._on_cancelled)

    @property
    def active_count(self) -> int:
        return len(self._tasks)

    def start(
        self,
        fn: Callable[[TaskContext], Any],
        *,
        on_success: Callable[[Any], None] | None = None,
        on_error: Callable[[BaseException], None] | None = None,
        on_progress: Callable[[int, int, str], None] | None = None,
        on_message: Callable[[str], None] | None = None,
        on_cancelled: Callable[[], None] | None = None,
        on_finished: Callable[[], None] | None = None,
    ) -> TaskHandle:
        task_id = next(self._ids)
        token = CancellationToken()
        handle = TaskHandle(task_id, token)
        self._tasks[task_id] = _Callbacks(
            on_success, on_error, on_progress, on_message, on_cancelled, on_finished, handle
        )
        self._pool.start(_Runnable(fn, TaskContext(task_id, self._bridge, token), self._bridge))
        return handle

    def cancel_all(self) -> None:
        for callbacks in self._tasks.values():
            if callbacks.handle is not None:
                callbacks.handle.cancel()

    def shutdown(self, timeout_ms: int = 5000) -> bool:
        """Cancel everything and wait (bounded) for workers. Returns True if all finished."""
        self.cancel_all()
        finished = self._pool.waitForDone(timeout_ms)
        if not finished:
            log.warning("%d task(s) still running at shutdown", self._pool.activeThreadCount())
        return finished

    # -- slots (GUI thread) ----------------------------------------------------------

    @Slot(int, int, int, str)
    def _on_progress(self, task_id: int, done: int, total: int, text: str) -> None:
        callbacks = self._tasks.get(task_id)
        if callbacks and callbacks.on_progress:
            callbacks.on_progress(done, total, text)

    @Slot(int, str)
    def _on_message(self, task_id: int, text: str) -> None:
        callbacks = self._tasks.get(task_id)
        if callbacks and callbacks.on_message:
            callbacks.on_message(text)

    @Slot(int, object)
    def _on_succeeded(self, task_id: int, result: object) -> None:
        self._finish(task_id, lambda c: c.on_success and c.on_success(result))

    @Slot(int, object)
    def _on_failed(self, task_id: int, error: object) -> None:
        def call(c: _Callbacks) -> None:
            if c.on_error:
                c.on_error(error)  # type: ignore[arg-type]
            else:
                log.error("Unhandled task error: %r", error)

        self._finish(task_id, call)

    @Slot(int)
    def _on_cancelled(self, task_id: int) -> None:
        self._finish(task_id, lambda c: c.on_cancelled and c.on_cancelled())

    def _finish(self, task_id: int, deliver: Callable[[_Callbacks], Any]) -> None:
        callbacks = self._tasks.pop(task_id, None)
        if callbacks is None:
            return
        if callbacks.handle is not None:
            callbacks.handle.running = False
        try:
            deliver(callbacks)
        finally:
            if callbacks.on_finished:
                callbacks.on_finished()
