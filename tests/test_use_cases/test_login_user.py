import pytest

from datetime import timedelta

from shortener.domain.services.token import Token
from shortener.domain.shared.datetime_utils import utc_now
from shortener.domain.user.exceptions import (
    UserEmailNotVerifiedError, UserNotFoundError, UserPasswordIncorrectError
)

from shortener.domain.user.user import User
from shortener.use_cases.login_user import LoginUserUseCase

from tests.fixtures.domain.users import UserFixture
from tests.fixtures.mocks import MockAuthTokenService


@pytest.fixture
def use_case(
    mock_user_repository,
    mock_password_hasher,
):
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
    return LoginUserUseCase(
        user_repository=mock_user_repository,
        password_hasher=mock_password_hasher,
        access_token_service=access_token_service,
        refresh_token_service=refresh_token_service
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
    assert isinstance(access_token, Token)

    user = await use_case.access_token_service.decode_token(access_token.value)
    assert user.email == normal_user.email


@pytest.mark.asyncio
async def test_retrieved_refresh_token(
    use_case: LoginUserUseCase, normal_user: UserFixture
):
    user = await use_case.user_repository.add(normal_user)
    
    retrieved = await use_case.execute(
        email=normal_user.email, 
        password=normal_user.mock_data["plain_password"]
    )

    refresh_token = retrieved["refresh_token"]
    assert isinstance(refresh_token, Token)
    
    user = await use_case.refresh_token_service.decode_token(refresh_token.value)
    assert user.email == normal_user.email


@pytest.mark.asyncio
async def test_retrieved_user(
    use_case: LoginUserUseCase, normal_user: UserFixture
):
    await use_case.user_repository.add(normal_user)
    retrieved = await use_case.execute(
        email=normal_user.email, 
        password=normal_user.mock_data["plain_password"]
    )

    user = retrieved["user"]
    assert isinstance(user, User)
    assert user.email == normal_user.email


@pytest.mark.asyncio
async def test_use_case_calls_ensure_user_can_login(
    use_case: LoginUserUseCase, unverified_email_user: UserFixture
):
    await use_case.user_repository.add(unverified_email_user)

    with pytest.raises(UserEmailNotVerifiedError):
        await use_case.execute(
            email=unverified_email_user.email,
            password=unverified_email_user.mock_data["plain_password"]
        )


@pytest.mark.asyncio
async def test_raises_user_not_found_error(
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
    assert (
        updated_user.last_login.replace(microsecond=0) ==
        utc_now().replace(microsecond=0)
    )
