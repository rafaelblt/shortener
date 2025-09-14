import pytest

from datetime import timedelta

from shortener.domain.services.token import Token, TokenInvalidError, TokenExpiredError

from shortener.domain.user.repository import UserRepository
from shortener.domain.user.user import User
from shortener.use_cases import RefreshLoginUseCase

from tests.fixtures.mocks.token import MockAuthTokenService


@pytest.fixture
def use_case(mock_user_repository):
    access_token_service = MockAuthTokenService(
        purpose="access",
        expires_in=timedelta(minutes=10),
        user_repository=mock_user_repository
    )
    refresh_token_service = MockAuthTokenService(
        purpose="refresh",
        expires_in=timedelta(days=7),
        user_repository=mock_user_repository,
    )
    return RefreshLoginUseCase(
        access_token_service=access_token_service,
        refresh_token_service=refresh_token_service
    )


@pytest.mark.asyncio
async def test_retrieved_access_token(
    use_case: RefreshLoginUseCase,
    normal_user: User,
    mock_user_repository: UserRepository
):
    normal_user = await mock_user_repository.add(normal_user)
    token = await use_case.refresh_token_service.generate_token(normal_user)

    retrieved = await use_case.execute(token.value)

    access_token = retrieved["access_token"]
    assert isinstance(access_token, Token)

    user = await use_case.access_token_service.decode_token(access_token.value)
    assert user.email == normal_user.email


@pytest.mark.asyncio
async def test_retrieved_refresh_token(
    use_case: RefreshLoginUseCase,
    normal_user: User,
    mock_user_repository: UserRepository
):
    normal_user = await mock_user_repository.add(normal_user)
    token = await use_case.refresh_token_service.generate_token(normal_user)

    retrieved = await use_case.execute(token.value)

    refresh_token = retrieved["refresh_token"]
    assert isinstance(refresh_token, Token)

    user = await use_case.refresh_token_service.decode_token(refresh_token.value)
    assert user.email == normal_user.email


@pytest.mark.asyncio
async def test_retrieved_user(
    use_case: RefreshLoginUseCase,
    normal_user: User,
    mock_user_repository: UserRepository
):
    normal_user = await mock_user_repository.add(normal_user)
    token = await use_case.refresh_token_service.generate_token(normal_user)

    retrieved = await use_case.execute(token.value)

    user = retrieved["user"]
    assert isinstance(user, User)
    assert user.email == normal_user.email


@pytest.mark.asyncio
async def test_with_refresh_token_invalid(use_case: RefreshLoginUseCase):
    with pytest.raises(TokenInvalidError):
        await use_case.execute("random")


@pytest.mark.asyncio
async def test_with_refresh_token_expired(
    use_case: RefreshLoginUseCase,
    normal_user: User,
    mock_user_repository: UserRepository
):
    assert isinstance(use_case.refresh_token_service, MockAuthTokenService)
    use_case.refresh_token_service._expires_in = timedelta(microseconds=1)

    normal_user = await mock_user_repository.add(normal_user)
    token = await use_case.refresh_token_service.generate_token(normal_user)

    with pytest.raises(TokenExpiredError):
        await use_case.execute(token.value)
