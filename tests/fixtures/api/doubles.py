from typing import Any
from unittest.mock import NonCallableMagicMock, create_autospec

import pytest

from shortener.api.authentication import AccessTokenVerifier
from shortener.api.health_check import HealthCheck
from shortener.api.rate_limit import RateLimiter
from shortener.domain import UserID
from shortener.use_cases.current_user import CurrentUser


ACCESS_TOKEN = "access-token"
AUTHORIZATION = {"Authorization": f"Bearer {ACCESS_TOKEN}"}


class UseCaseDoubles:
    """
    A UseCaseFactory that builds a double of each use case, the same one on
    every request, and keeps the current users it was given. A test sets what
    execute() of a double returns, and checks how it was awaited.
    """

    def __init__(self) -> None:
        self.current_users: list[CurrentUser] = []
        self._doubles: dict[type, NonCallableMagicMock] = {}

    def build(self, use_case: type, current_user: CurrentUser) -> Any:
        self.current_users.append(current_user)
        return self.double(use_case)

    def double(self, use_case: type) -> NonCallableMagicMock:
        if use_case not in self._doubles:
            self._doubles[use_case] = create_autospec(use_case, instance=True)
        return self._doubles[use_case]


@pytest.fixture
def use_cases() -> UseCaseDoubles:
    return UseCaseDoubles()


@pytest.fixture
def access_token_verifier(owner_id: UserID) -> NonCallableMagicMock:
    """Takes any token as one issued to owner_id."""
    verifier = create_autospec(AccessTokenVerifier, instance=True)
    verifier.verify.return_value = owner_id
    return verifier


@pytest.fixture
def rate_limiter() -> NonCallableMagicMock:
    """Lets every request through."""
    rate_limiter = create_autospec(RateLimiter, instance=True)
    rate_limiter.hit.return_value = None
    return rate_limiter


@pytest.fixture
def health_check() -> NonCallableMagicMock:
    """Passes, unless a test sets check() to raise."""
    return create_autospec(HealthCheck, instance=True)
