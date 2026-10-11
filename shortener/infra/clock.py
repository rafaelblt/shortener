from datetime import datetime, timezone


class UTCClock:

    def now(self) -> datetime:
        return datetime.now(timezone.utc)
