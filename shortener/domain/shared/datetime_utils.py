from datetime import datetime, timezone


def is_utc(dt: datetime) -> bool:
    return (
        dt.tzinfo is not None and 
        dt.tzinfo.utcoffset(dt) == timezone.utc.utcoffset(dt)
    )


def ensure_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt
