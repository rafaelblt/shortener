import pytest

from shortener.domain.user import User
from shortener.domain.user.fields import HashedPassword
from shortener.domain.user.exceptions import (
    UserNotFoundInDatabaseError, UserPasswordIncorrectError
)

from shortener.use_cases.login_user import LoginUserUseCase


@pytest.fixture
def use_case(mock_user_repository, mock_password_hasher, mock_auth_token_service):
    return LoginUserUseCase(
        user_repository=mock_user_repository,
        password_hasher=mock_password_hasher,
        auth_token_service=mock_auth_token_service
    )


@pytest.mark.asyncio
async def test_retrieved_token(use_case: LoginUserUseCase, normal_user: User):
    normal_user.change_hashed_password(
        HashedPassword(use_case.password_hasher.hash("pass123"))
    )

    await use_case.user_repository.add(normal_user)
    token = await use_case.execute(email=normal_user.email, password="pass123")

    assert use_case.auth_token_service.decode_token(token) == normal_user.email


@pytest.mark.asyncio
async def test_raises_user_not_found_in_database(
    use_case: LoginUserUseCase, normal_user: User
):
    with pytest.raises(UserNotFoundInDatabaseError) as error:
        await use_case.execute(email=normal_user.email, password="123")
    assert error.value.value == normal_user.email
    assert error.value.field == "email"


@pytest.mark.asyncio
async def test_raises_user_password_incorrect(
    use_case: LoginUserUseCase, normal_user: User
):
    normal_user.change_hashed_password(
        HashedPassword(use_case.password_hasher.hash("pass123"))
    )
    await use_case.user_repository.add(normal_user)

    with pytest.raises(UserPasswordIncorrectError):
        await use_case.execute(email=normal_user.email, password="123")
