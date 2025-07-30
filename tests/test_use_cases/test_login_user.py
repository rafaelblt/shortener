import pytest

from datetime import timedelta

from shortener.domain.services.token import TokenService
from shortener.domain.services.token import RandomTokenGenerator
from shortener.domain.shared.datetime_utils import utc_now
from shortener.domain.user.exceptions import (
    UserEmailNotVerifiedError, UserNotFoundError, UserPasswordIncorrectError
)

from shortener.domain.user.user import User
from shortener.use_cases.login_user import LoginUserUseCase

from tests.fixtures import UserFixture
from tests.utils.date_helpers import assert_datetime


ACCESS_TOKEN_EXPIRES_IN = timedelta(minutes=10)
REFRESH_TOKEN_EXPIRES_IN = timedelta(hours=24)


@pytest.fixture
def use_case(
    mock_user_repository,
    mock_refresh_token_repository,
    mock_password_hasher,
    mock_token_service
):
    class Generator(RandomTokenGenerator):
        def generate_token(self) -> str:
            return "random"

    return LoginUserUseCase(
        user_repository=mock_user_repository,
        refresh_token_repository=mock_refresh_token_repository,
        password_hasher=mock_password_hasher,
        access_token_service=mock_token_service,
        access_token_expires_in=ACCESS_TOKEN_EXPIRES_IN,
        refresh_token_generator=Generator(),
        refresh_token_expires_in=REFRESH_TOKEN_EXPIRES_IN
    )


@pytest.mark.asyncio
async def test_retrieved_access_token(
    use_case: LoginUserUseCase, normal_user: UserFixture
):
    await use_case.user_repository.add(normal_user)
    retrieved = await use_case.execute(
        email=normal_user.email, 
        password=normal_user.mock_data["plain_password"]
    )

    access_token = retrieved["access_token"]

    payload = use_case.access_token_service.decode_token(access_token)
    
    assert payload["subject"] == normal_user.email
    assert payload["purpose"] == TokenService.Purpose.LOGIN
    assert_datetime(
        payload["expires_at"], utc_now() + ACCESS_TOKEN_EXPIRES_IN,
        year=True, month=True, day=True, hour=True, minute=True
    )


@pytest.mark.asyncio
async def test_retrieved_refresh_token(
    use_case: LoginUserUseCase, normal_user: UserFixture
):
    user = await use_case.user_repository.add(normal_user)
    
    retrieved = await use_case.execute(
        email=normal_user.email, 
        password=normal_user.mock_data["plain_password"]
    )

    token = retrieved["refresh_token"]
    refresh_token = await use_case.refresh_token_repository.get_by_token(token)
    assert refresh_token is not None
    assert refresh_token.user.pk == user.pk
    assert_datetime(
        refresh_token.expires_at, utc_now() + REFRESH_TOKEN_EXPIRES_IN,
        year=True, month=True, day=True, hour=True, minute=True
    )


@pytest.mark.asyncio
async def test_use_case_calls_ensure_user_can_login(
    use_case: LoginUserUseCase, unverified_email_user: User
):
    await use_case.user_repository.add(unverified_email_user)

    with pytest.raises(UserEmailNotVerifiedError):
        await use_case.execute(
            email=unverified_email_user.email,
            password="unnecessary"
        )


@pytest.mark.asyncio
async def test_raises_user_not_found_in_database(
    use_case: LoginUserUseCase, normal_user: UserFixture
):
    with pytest.raises(UserNotFoundError) as error:
        await use_case.execute(
            email=normal_user.email,
            password=normal_user.mock_data["plain_password"]
        )
    assert error.value.value == normal_user.email
    assert error.value.field == "email"


@pytest.mark.asyncio
async def test_raises_user_password_incorrect(
    use_case: LoginUserUseCase, normal_user: UserFixture
):
    await use_case.user_repository.add(normal_user)

    with pytest.raises(UserPasswordIncorrectError):
        await use_case.execute(
            email=normal_user.email,
            password="1"
        )


@pytest.mark.asyncio
async def test_user_last_login(
    use_case: LoginUserUseCase, normal_user: UserFixture
):
    await use_case.user_repository.add(normal_user)

    await use_case.execute(
        email=normal_user.email, 
        password=normal_user.mock_data["plain_password"]
    )

    updated_user = await use_case.user_repository.get_by_email(normal_user.email)
    assert updated_user is not None
    assert updated_user.last_login is not None
    assert_datetime(
        updated_user.last_login, utc_now(),
        year=True, month=True, day=True, hour=True, minute=True
    )
