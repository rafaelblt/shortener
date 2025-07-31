import pytest

from datetime import timedelta

from shortener.domain.services.token import TokenService, TokenInvalidError, TokenExpiredError

from shortener.domain.user import User
from shortener.domain.user.fields import UserStatus
from shortener.domain.user.exceptions import (
    UserNotFoundError, UserStatusInvalidToVerifyEmailError
)

from shortener.use_cases import VerifyEmailUseCase

from tests.fixtures import MockTokenService


def get_email_verification_token(user: User):
    return MockTokenService().generate_token(
        subject=user.email,
        purpose=TokenService.Purpose.EMAIL_VERIFICATION,
        expires_in=timedelta(minutes=10),
    )


@pytest.fixture
def use_case(mock_user_repository, mock_token_service):
    return VerifyEmailUseCase(
        user_repository=mock_user_repository,
        token_service=mock_token_service
    )


@pytest.mark.asyncio
async def test_if_user_status_is_updated(
    use_case: VerifyEmailUseCase,
    unverified_email_user: User
):
    user = unverified_email_user
    await use_case.user_repository.add(user)

    token = get_email_verification_token(unverified_email_user)
    retrieved = await use_case.execute(token=token)
    assert retrieved is None

    user = await use_case.user_repository.get_by_email(user.email)
    assert user is not None
    assert user.status is UserStatus.ACTIVE


@pytest.mark.asyncio
async def test_with_invalid_token_format(use_case: VerifyEmailUseCase):
    with pytest.raises(TokenInvalidError):
        await use_case.execute("invalid-token")


@pytest.mark.asyncio
async def test_with_invalid_token_purpose(
    use_case: VerifyEmailUseCase,
    unverified_email_user: User
):
    token = MockTokenService().generate_token(
        subject=unverified_email_user.email,
        purpose="other_purpose", # type: ignore
        expires_in=timedelta(minutes=5),
    )
    with pytest.raises(TokenInvalidError):
        await use_case.execute(token)


@pytest.mark.asyncio
async def test_with_invalid_user_status(
    use_case: VerifyEmailUseCase, normal_user: User
):
    user = normal_user
    await use_case.user_repository.add(user)
    token = get_email_verification_token(user)

    with pytest.raises(UserStatusInvalidToVerifyEmailError):
        await use_case.execute(token)


@pytest.mark.asyncio
async def test_with_non_existent_email(
    use_case: VerifyEmailUseCase, normal_user: User
):
    token = get_email_verification_token(normal_user)

    with pytest.raises(UserNotFoundError) as error:
        await use_case.execute(token)

    assert error.value.field == "email"
    assert error.value.value == normal_user.email
