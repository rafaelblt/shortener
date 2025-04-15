from datetime import datetime, timezone


def is_utc(dt: datetime) -> bool:
    return (
        dt.tzinfo is not None and 
        dt.tzinfo.utcoffset(dt) == timezone.utc.utcoffset(dt)
    )
