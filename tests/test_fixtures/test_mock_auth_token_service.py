import pytest

from datetime import datetime, timedelta

from shortener.domain.services.exceptions import TokenExpiredError, TokenInvalidError
from shortener.domain.services.token import AuthTokenService
from shortener.domain.shared.primarykey import PrimaryKey
from shortener.domain.shared.token import Token
from shortener.domain.shared.datetime_utils import utc_now
from shortener.domain.user import User

from tests.fixtures import MockAuthTokenService
from tests.utils.date_helpers import assert_datetime


PURPOSE = "mock_purpose"
EXPIRES_IN = timedelta(days=1)


@pytest.fixture
def service(mock_user_repository):
    return MockAuthTokenService(
        purpose=PURPOSE,
        expires_in=EXPIRES_IN,
        user_repository=mock_user_repository,
    )


def test_inheritance(service: MockAuthTokenService):
    assert isinstance(service, AuthTokenService)


@pytest.mark.asyncio
async def test_generate_token(service: MockAuthTokenService, normal_user: User):
    token = await service.generate_token(normal_user)
    assert isinstance(token, Token)
    assert isinstance(token.value, str)
    assert token.purpose == PURPOSE
    assert token.created_at.replace(microsecond=0) == utc_now().replace(microsecond=0)


@pytest.mark.asyncio
async def test_decode_token(service: MockAuthTokenService, normal_user: User):
    normal_user = await service._user_repo.add(normal_user)
    token = await service.generate_token(normal_user)

    retrieved = await service.decode_token(token.value)
    assert retrieved.email == normal_user.email


@pytest.mark.asyncio
async def test_decode_random_token_raises_invalid_error(service: MockAuthTokenService):
    with pytest.raises(TokenInvalidError):
        await service.decode_token("random")


@pytest.mark.asyncio
async def test_decode_token_user_non_existent_raises_invalid_error(
    service: MockAuthTokenService, normal_user: User
):
    normal_user._pk = PrimaryKey.create_pk_id(1)
    token = await service.generate_token(normal_user)
    with pytest.raises(TokenInvalidError):
        await service.decode_token(token.value)


@pytest.mark.asyncio
async def test_decode_token_with_different_purpose_raises_invalid_error(
    service: MockAuthTokenService, normal_user: User
):
    normal_user = await service._user_repo.add(normal_user)
    token = await service.generate_token(normal_user)
    service._purpose = "different_purpose"
    with pytest.raises(TokenInvalidError):
        await service.decode_token(token.value)


@pytest.mark.asyncio
async def test_decode_token_raises_expired_error(
    service: MockAuthTokenService, normal_user: User
):
    service._expires_in = timedelta(microseconds=1)
    token = await service.generate_token(normal_user)
    with pytest.raises(TokenExpiredError):
        await service.decode_token(token.value)


@pytest.mark.asyncio
async def test_mock_data(service: MockAuthTokenService, normal_user: User):
    assert len(service.mock_data["generated_tokens"]) == 0

    token = await service.generate_token(normal_user)
    
    assert len(service.mock_data["generated_tokens"]) == 1
    assert service.mock_data["generated_tokens"][0]["token"] == token.value
