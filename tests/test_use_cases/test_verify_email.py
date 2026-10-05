import pytest

from datetime import timedelta

from shortener.domain.services.token import TokenInvalidError, TokenExpiredError

from shortener.domain.shared.primarykey import PrimaryKey
from shortener.domain.user import User
from shortener.domain.user.fields import UserStatus
from shortener.domain.user.exceptions import UserStatusInvalidToVerifyEmailError

from shortener.use_cases import VerifyEmailUseCase

from tests.fixtures.mocks import MockAuthTokenService


def get_email_verification_token(user: User): ...


@pytest.fixture
def use_case(mock_user_repository):
    token_service = MockAuthTokenService(
        purpose="verify_email",
        expires_in=timedelta(days=1),
        user_repository=mock_user_repository
    )
    return VerifyEmailUseCase(
        user_repository=mock_user_repository,
        token_service=token_service
    )


@pytest.mark.asyncio
async def test_if_user_status_is_updated(
    use_case: VerifyEmailUseCase,
    unverified_email_user: User
):
    user = await use_case.user_repository.add(unverified_email_user)
    token = await use_case.token_service.generate_token(user)

    retrieved = await use_case.execute(token=token.value)
    assert retrieved is None

    user = await use_case.user_repository.get_by_email(user.email)
    assert user is not None
    assert user.status is UserStatus.ACTIVE


@pytest.mark.asyncio
async def test_with_invalid_token(use_case: VerifyEmailUseCase):
    with pytest.raises(TokenInvalidError):
        await use_case.execute("invalid-token")


@pytest.mark.asyncio
async def test_with_invalid_user_status(
    use_case: VerifyEmailUseCase, normal_user: User
):
    user = await use_case.user_repository.add(normal_user)
    token = await use_case.token_service.generate_token(user)

    with pytest.raises(UserStatusInvalidToVerifyEmailError):
        await use_case.execute(token.value)


@pytest.mark.asyncio
async def test_with_non_existent_email(
    use_case: VerifyEmailUseCase, normal_user: User
):
    normal_user._pk = PrimaryKey.create_pk_id(1)
    token = await use_case.token_service.generate_token(normal_user)

    with pytest.raises(TokenInvalidError):
        await use_case.execute(token.value)


@pytest.mark.asyncio
async def test_with_token_expired(
    use_case: VerifyEmailUseCase, normal_user: User
):
    assert isinstance(use_case.token_service, MockAuthTokenService)
    use_case.token_service._expires_in = timedelta(microseconds=1)

    user = await use_case.user_repository.add(normal_user)
    token = await use_case.token_service.generate_token(user)

    with pytest.raises(TokenExpiredError):
        await use_case.execute(token.value)
