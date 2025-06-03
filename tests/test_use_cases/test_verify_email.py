import pytest

from shortener.domain.services.auth_token import AuthTokenService
from shortener.domain.services.exceptions import AuthTokenInvalidError

from shortener.domain.user import User
from shortener.domain.user.fields import UserStatus
from shortener.domain.user.exceptions import (
    UserNotFoundError, UserStatusInvalidToVerifyEmailError
)

from shortener.use_cases import VerifyEmailUseCase


@pytest.fixture
def use_case(mock_user_repository, mock_auth_token_service):
    return VerifyEmailUseCase(
        user_repository=mock_user_repository,
        auth_token_service=mock_auth_token_service
    )


@pytest.mark.asyncio
async def test_if_user_status_is_updated(
    use_case: VerifyEmailUseCase, unverified_email_user: User
):
    user = unverified_email_user
    await use_case.user_repository.add(user)
    token = use_case.auth_token_service.generate_token(user.email)

    retrieved = await use_case.execute(token=token)
    assert retrieved is None

    user = await use_case.user_repository.get_by_email(user.email)
    assert user is not None
    assert user.status is UserStatus.ACTIVE


@pytest.mark.asyncio
async def test_with_invalid_token(use_case: VerifyEmailUseCase):
    with pytest.raises(AuthTokenInvalidError):
        await use_case.execute("invalid-token")


@pytest.mark.asyncio
async def test_with_invalid_user_status(
    use_case: VerifyEmailUseCase, normal_user: User
):
    user = normal_user
    await use_case.user_repository.add(user)
    token = use_case.auth_token_service.generate_token(user.email)

    with pytest.raises(UserStatusInvalidToVerifyEmailError):
        await use_case.execute(token)


@pytest.mark.asyncio
async def test_with_non_existent_email(
    use_case: VerifyEmailUseCase, normal_user: User
):
    token = use_case.auth_token_service.generate_token(normal_user.email)

    with pytest.raises(UserNotFoundError) as error:
        await use_case.execute(token)

    assert error.value.field == "email"
    assert error.value.value == normal_user.email
