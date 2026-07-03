from __future__ import annotations

import logging
import time

logger = logging.getLogger(__name__)


class ProgressTracker:
    def __init__(self, total: int, label: str = "items") -> None:
        self.total = total
        self.label = label
        self._done = 0
        self._start = time.perf_counter()

    def update(self, n: int = 1) -> None:
        self._done += n
        pct = 100 * self._done / max(self.total, 1)
        elapsed = time.perf_counter() - self._start
        logger.debug("Progress: %d/%d (%.0f%%) %.1fs", self._done, self.total, pct, elapsed)

    @property
    def done(self) -> int:
        return self._done

    @property
    def remaining(self) -> int:
        return max(0, self.total - self._done)

    @property
    def pct(self) -> float:
        return round(100 * self._done / max(self.total, 1), 1)

    @property
    def elapsed_s(self) -> float:
        return round(time.perf_counter() - self._start, 2)
