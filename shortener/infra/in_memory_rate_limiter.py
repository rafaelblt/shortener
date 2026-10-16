from datetime import datetime, timedelta

from shortener.use_cases.clock import Clock


class InMemoryRateLimiter:
    """
    Allows each key up to a number of requests in each window of time, and
    counts them in the memory of the process. See docs/architecture/infra.md#rate-limit
    """

    def __init__(self, requests: int, window: timedelta, clock: Clock):
        self._requests = requests
        self._window = window
        self._clock = clock
        self._window_end: datetime | None = None
        self._counts: dict[str, int] = {}

    def hit(self, key: str) -> timedelta | None:
        now = self._clock.now()
        if self._window_end is None or now >= self._window_end:
            # Forgetting the counts of the window that ended keeps only the
            # keys of the current one in memory.
            self._window_end = now + self._window
            self._counts.clear()
        self._counts[key] = self._counts.get(key, 0) + 1
        if self._counts[key] > self._requests:
            return self._window_end - now
        return None
