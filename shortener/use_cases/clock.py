from datetime import datetime
from typing import Protocol


class Clock(Protocol):
    def now(self) -> datetime:
        """Returns the current moment, as a timezone-aware datetime."""
        ...
