import pytest

from datetime import datetime, timedelta
from unittest.mock import NonCallableMagicMock, create_autospec

from shortener.infra.in_memory_rate_limiter import InMemoryRateLimiter
from shortener.use_cases.clock import Clock


REQUESTS = 3
WINDOW = timedelta(seconds=60)
KEY = "203.0.113.7"
OTHER_KEY = "198.51.100.20"


@pytest.fixture
def clock(now: datetime) -> NonCallableMagicMock:
    clock = create_autospec(Clock, instance=True)
    clock.now.return_value = now
    return clock


@pytest.fixture
def rate_limiter(clock: NonCallableMagicMock) -> InMemoryRateLimiter:
    return InMemoryRateLimiter(REQUESTS, WINDOW, clock)


def hit(
    rate_limiter: InMemoryRateLimiter, key: str, times: int
) -> list[timedelta | None]:
    return [rate_limiter.hit(key) for _ in range(times)]


def test_hit_allows_the_requests_of_a_key_up_to_the_limit(
    rate_limiter: InMemoryRateLimiter,
):
    assert hit(rate_limiter, KEY, REQUESTS) == [None] * REQUESTS


@pytest.mark.parametrize(
    "elapsed, retry_after",
    [
        pytest.param(timedelta(0), WINDOW, id="start of the window"),
        pytest.param(timedelta(seconds=20), timedelta(seconds=40), id="middle"),
        pytest.param(
            WINDOW - timedelta(microseconds=1),
            timedelta(microseconds=1),
            id="last moment",
        ),
        pytest.param(WINDOW, None, id="end of the window"),
    ],
)
def test_hit_refuses_a_request_over_the_limit_until_the_window_ends(
    rate_limiter: InMemoryRateLimiter,
    clock: NonCallableMagicMock,
    now: datetime,
    elapsed: timedelta,
    retry_after: timedelta | None,
):
    hit(rate_limiter, KEY, REQUESTS)
    clock.now.return_value = now + elapsed

    assert rate_limiter.hit(KEY) == retry_after


def test_hit_counts_each_key_apart(rate_limiter: InMemoryRateLimiter):
    hit(rate_limiter, KEY, REQUESTS)
    assert rate_limiter.hit(OTHER_KEY) is None


def test_hit_counts_every_key_in_the_same_window(
    rate_limiter: InMemoryRateLimiter, clock: NonCallableMagicMock, now: datetime
):
    rate_limiter.hit(KEY)
    clock.now.return_value = now + timedelta(seconds=50)
    hit(rate_limiter, OTHER_KEY, REQUESTS)

    assert rate_limiter.hit(OTHER_KEY) == timedelta(seconds=10)


def test_hit_starts_a_window_at_the_first_request_after_the_last_one_ended(
    rate_limiter: InMemoryRateLimiter, clock: NonCallableMagicMock, now: datetime
):
    hit(rate_limiter, KEY, REQUESTS + 1)
    clock.now.return_value = now + WINDOW + timedelta(seconds=30)

    assert hit(rate_limiter, KEY, REQUESTS + 1) == [None] * REQUESTS + [WINDOW]
