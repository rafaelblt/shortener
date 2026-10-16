from collections.abc import Awaitable, Callable
from datetime import timedelta
from typing import Protocol

from fastapi import Request


class RateLimiter(Protocol):
    def hit(self, key: str) -> timedelta | None:
        """
        Counts a request of the key. Returns None when the key is within its
        limit, and otherwise how long until it can make requests again.
        """
        ...


class TooManyRequestsError(Exception):
    """The client made more requests than its limit."""

    def __init__(self, retry_after: timedelta):
        super().__init__(f"The client can make requests again in {retry_after}")
        self.retry_after = retry_after


def limit_by_ip(rate_limiter: RateLimiter) -> Callable[[Request], Awaitable[None]]:
    """
    A dependency of FastAPI that counts each request under the IP address of
    its client. See docs/architecture/api.md#rate-limit
    """

    # Async, so FastAPI runs it in the event loop, and not in a thread, where
    # two requests could count at the same time.
    async def limit(request: Request) -> None:
        """
        Raises:
            TooManyRequestsError: The IP address is over its limit.
        """
        if request.client is None:
            return
        retry_after = rate_limiter.hit(request.client.host)
        if retry_after is not None:
            raise TooManyRequestsError(retry_after)

    return limit
