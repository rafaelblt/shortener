from datetime import datetime, timedelta, timezone

from shortener.infra.clock import UTCClock


def test_now_returns_the_current_moment_in_utc():
    before = datetime.now(timezone.utc)
    now = UTCClock().now()
    after = datetime.now(timezone.utc)

    assert before <= now <= after
    assert now.utcoffset() == timedelta(0)
