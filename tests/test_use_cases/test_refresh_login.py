import pytest

from datetime import timedelta

from shortener.domain.refresh_token.entity import RefreshToken
from shortener.domain.refresh_token.exceptions import (
    RefreshTokenExpiredError, RefreshTokenRevokedError
)

from shortener.domain.services.token import TokenService
from shortener.domain.services.token import RandomTokenGenerator
from shortener.domain.shared.datetime_utils import utc_now

from shortener.domain.user.user import User
from shortener.use_cases import RefreshLoginUseCase

from tests.utils.date_helpers import assert_datetime


ACCESS_TOKEN_EXPIRES_IN = timedelta(minutes=10)
REFRESH_TOKEN_EXPIRES_IN = timedelta(hours=24)


@pytest.fixture
def use_case(
    mock_refresh_token_repository,
    mock_token_service
):
    class Generator(RandomTokenGenerator):
        def generate_token(self) -> str:
            return "random"

    return RefreshLoginUseCase(
        refresh_token_repository=mock_refresh_token_repository,
        access_token_service=mock_token_service,
        access_token_expires_in=ACCESS_TOKEN_EXPIRES_IN,
        refresh_token_generator=Generator(),
        refresh_token_expires_in=REFRESH_TOKEN_EXPIRES_IN
    )


@pytest.mark.asyncio
async def test_retrieved_access_token(
    use_case: RefreshLoginUseCase,
    active_refresh_token: RefreshToken
):
    await use_case.refresh_token_repository.add(active_refresh_token)

    retrieved = await use_case.execute(active_refresh_token.token)

    access_token = retrieved["access_token"]

    payload = use_case.access_token_service.decode_token(access_token)
    
    assert payload["subject"] == active_refresh_token.user.email
    assert payload["purpose"] == TokenService.Purpose.LOGIN
    assert_datetime(
        payload["expires_at"], utc_now() + ACCESS_TOKEN_EXPIRES_IN,
        year=True, month=True, day=True, hour=True, minute=True
    )


@pytest.mark.asyncio
async def test_retrieved_new_refresh_token(
    use_case: RefreshLoginUseCase,
    active_refresh_token: RefreshToken
):
    await use_case.refresh_token_repository.add(active_refresh_token)
    
    retrieved = await use_case.execute(active_refresh_token.token)

    refresh_token = retrieved["refresh_token"]
    assert isinstance(refresh_token, RefreshToken)
    assert refresh_token.user.email == active_refresh_token.user.email
    assert_datetime(
        refresh_token.expires_at, utc_now() + REFRESH_TOKEN_EXPIRES_IN,
        year=True, month=True, day=True, hour=True, minute=True
    )


@pytest.mark.asyncio
async def test_if_used_refresh_token_is_consumed(
    use_case: RefreshLoginUseCase,
    active_refresh_token: RefreshToken
):
    await use_case.refresh_token_repository.add(active_refresh_token)
    
    await use_case.execute(active_refresh_token.token)
    
    refresh_token = await use_case.refresh_token_repository.get_by_token(
        active_refresh_token.token
    )

    assert refresh_token is not None
    assert refresh_token.is_revoked()


@pytest.mark.asyncio
async def test_if_new_refresh_token_is_saved(
    use_case: RefreshLoginUseCase,
    active_refresh_token: RefreshToken
):
    await use_case.refresh_token_repository.add(active_refresh_token)
    
    retrieved = await use_case.execute(active_refresh_token.token)
    refresh_token = retrieved["refresh_token"]

    saved_token = await use_case.refresh_token_repository.get_by_token(
        refresh_token.token
    )
    assert saved_token is not None
    assert saved_token.pk.get_id() == refresh_token.pk.get_id()
    assert saved_token.user.email == active_refresh_token.user.email


@pytest.mark.asyncio
async def test_retrieved_user(
    use_case: RefreshLoginUseCase,
    active_refresh_token: RefreshToken
):
    await use_case.refresh_token_repository.add(active_refresh_token)

    retrieved = await use_case.execute(active_refresh_token.token)

    user = retrieved["user"]
    assert isinstance(user, User)
    assert user.email == active_refresh_token.user.email


@pytest.mark.asyncio
async def test_with_refresh_token_revoked(
    use_case: RefreshLoginUseCase,
    revoked_refresh_token: RefreshToken
):
    await use_case.refresh_token_repository.add(revoked_refresh_token)

    with pytest.raises(RefreshTokenRevokedError):
        await use_case.execute(revoked_refresh_token.token)


@pytest.mark.asyncio
async def test_with_refresh_token_expired(
    use_case: RefreshLoginUseCase,
    expired_refresh_token: RefreshToken
):
    await use_case.refresh_token_repository.add(expired_refresh_token)

    with pytest.raises(RefreshTokenExpiredError):
        await use_case.execute(expired_refresh_token.token)
