"""Core countdown logic for MonkeyTimer.

The class in this module has no Tkinter dependency, so it can be tested without
opening a graphical window.
"""

from __future__ import annotations

import math
import time
from typing import Callable


class CountdownTimer:
    """A pauseable countdown driven by a monotonic clock."""

    def __init__(self, clock: Callable[[], float] = time.monotonic) -> None:
        self._clock = clock
        self._duration = 0.0
        self._remaining = 0.0
        self._started_at: float | None = None
        self._paused = False

    @property
    def is_running(self) -> bool:
        self._update()
        return self._started_at is not None

    @property
    def is_paused(self) -> bool:
        return self._paused

    @property
    def has_duration(self) -> bool:
        return self._duration > 0

    def start(self, duration_seconds: int) -> None:
        if duration_seconds <= 0:
            raise ValueError("倒计时时间必须大于 0。")
        self._duration = float(duration_seconds)
        self._remaining = self._duration
        self._started_at = self._clock()
        self._paused = False

    def pause(self) -> None:
        if not self.is_running:
            return
        self._update()
        if self._started_at is None:
            return
        self._started_at = None
        self._paused = True

    def resume(self) -> None:
        if self._paused and self._remaining > 0:
            self._started_at = self._clock()
            self._paused = False

    def reset(self) -> None:
        self._remaining = self._duration
        self._started_at = None
        self._paused = False

    def remaining_seconds(self) -> float:
        self._update()
        return self._remaining

    def display_seconds(self) -> int:
        """Return seconds for display, rounding a partial second up."""
        return math.ceil(self.remaining_seconds())

    def _update(self) -> None:
        if self._started_at is None:
            return
        elapsed = self._clock() - self._started_at
        self._remaining = max(0.0, self._remaining - elapsed)
        self._started_at = self._clock()
        if self._remaining == 0:
            self._started_at = None
            self._paused = False
