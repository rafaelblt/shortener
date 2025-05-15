import pytest

from datetime import datetime

from shortener.domain.services.auth_token import AuthTokenService
from shortener.domain.services.exceptions import (
    AuthTokenInvalidError,
    AuthTokenExpiredError
)

from tests.fixtures import MockAuthTokenService


@pytest.fixture
def service(mock_auth_token_service):
    return mock_auth_token_service


def test_inheritance(service: MockAuthTokenService):
    assert isinstance(service, AuthTokenService)


def test_generate_token(service: MockAuthTokenService):
    subject = "user123"
    token = service.generate_token(subject=subject)
    assert isinstance(token, str)
    token_split = token.split("|")
    assert len(token_split) == 3
    assert token_split[0] == subject
    assert token_split[1] == service.secret_key
    assert datetime.fromtimestamp(float(token_split[2]))


def test_decode_token(service: MockAuthTokenService):
    subject = "user123"
    token = service.generate_token(subject=subject)

    decoded = service.decode_token(token)
    assert decoded == subject


def test_decode_token_raises_invalid_error(service: MockAuthTokenService):
    subject = "user123"
    token = service.generate_token(subject)
    
    with pytest.raises(AuthTokenInvalidError):
        invalid_token_format = str(token.split("|"))
        service.decode_token(invalid_token_format)
    with pytest.raises(AuthTokenInvalidError):
        token_split = token.split("|")
        token_split[1] = "new_secret_key"
        invalid_token_key = "|".join(token_split)
        service.decode_token(invalid_token_key)


def test_decode_token_raises_expired_error():
    subject = "user123"
    short_token_service = MockAuthTokenService(expires_minutes=0)

    token = short_token_service.generate_token(subject)

    with pytest.raises(AuthTokenExpiredError):
        short_token_service.decode_token(token)
