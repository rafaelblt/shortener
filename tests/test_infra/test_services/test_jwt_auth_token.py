import pytest

from shortener.domain.services.exceptions import (
    AuthTokenExpiredError, AuthTokenInvalidError
)
from shortener.infra.settings import (
    JWT_AUTH_SECRET_KEY,
    JWT_AUTH_TOKEN_ALGORITHM,
    JWT_AUTH_TOKEN_EXPIRES_MINUTES
)

from shortener.infra.services.jwt_auth_token import JwtAuthTokenService


@pytest.fixture
def service():
    return JwtAuthTokenService()


def test_attr_default_secret_key(service: JwtAuthTokenService):
    assert hasattr(service, "secret_key")
    assert service._secret_key == JWT_AUTH_SECRET_KEY


def test_attr_default_algorithm(service: JwtAuthTokenService):
    assert hasattr(service, "algorithm")
    assert service._algorithm == JWT_AUTH_TOKEN_ALGORITHM


def test_attr_default_expires_minutes(service: JwtAuthTokenService):
    assert hasattr(service, "expires_minutes")
    assert service.expires_minutes == JWT_AUTH_TOKEN_EXPIRES_MINUTES


def test_method_generate_token(service: JwtAuthTokenService):
    subject = "user123"
    token = service.generate_token(subject=subject)
    assert isinstance(token, str)


def test_method_decode_token(service: JwtAuthTokenService):
    subject = "user123"
    token = service.generate_token(subject=subject)

    decoded = service.decode_token(token)
    assert decoded == subject


def test_method_decode_token_raises_invalid_error():
    subject = "user123"

    service1 = JwtAuthTokenService(secret_key="key1")
    service2 = JwtAuthTokenService(secret_key="key2") 

    token = service1.generate_token(subject)
    with pytest.raises(AuthTokenInvalidError):
        service2.decode_token(token)


def test_method_decode_token_raises_expired_error():
    subject = "user123"
    short_token_service = JwtAuthTokenService(expires_minutes=0)

    token = short_token_service.generate_token(subject)

    with pytest.raises(AuthTokenExpiredError):
        short_token_service.decode_token(token)
