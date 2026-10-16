from datetime import UTC, datetime, timedelta

from shortener.infra.clock import UTCClock


def test_now_returns_the_current_moment_in_utc():
    before = datetime.now(UTC)
    now = UTCClock().now()
    after = datetime.now(UTC)

    assert before <= now <= after
    assert now.utcoffset() == timedelta(0)
