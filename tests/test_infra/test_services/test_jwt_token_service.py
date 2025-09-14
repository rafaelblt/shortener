from datetime import timedelta
import pytest

from shortener.domain.services.exceptions import TokenInvalidError
from shortener.domain.services.token import Token, TokenService, TokenExpiredError
from shortener.domain.shared.datetime_utils import utc_now
from shortener.infra.services.jwt_token import JwtTokenService


@pytest.fixture
def service():
    return JwtTokenService()


def test_inheritance(service: JwtTokenService):
    assert isinstance(service, TokenService)


def test_generate_token(service: JwtTokenService):
    retrieved = service.generate_token(
        "subject", "purpose", timedelta(seconds=1)
    )

    assert isinstance(retrieved, Token)
    assert isinstance(retrieved.value, str)
    assert retrieved.purpose == "purpose"
    assert (
        retrieved.created_at.replace(microsecond=0) ==
        utc_now().replace(microsecond=0)
    )
    assert retrieved.expires_at == retrieved.created_at + timedelta(seconds=1)


def test_decode_token(service: JwtTokenService):
    subject = "subject123"
    purpose = "purpose123"
    expires_in = timedelta(minutes=1)

    token = service.generate_token(subject, purpose, expires_in)

    decoded = service.decode_token(token.value)

    assert decoded["subject"] == subject
    assert decoded["purpose"] == purpose
    assert (
        decoded["created_at"].replace(microsecond=0) ==
        utc_now().replace(microsecond=0)
    )
    assert decoded["expires_at"] == decoded["created_at"] + expires_in
    assert decoded["extra_claims"] == {}


def test_decode_token_raises_expired_error(service: JwtTokenService):
    expires_in = timedelta(microseconds=1)
    token = service.generate_token("subject", "purpose", expires_in)
    with pytest.raises(TokenExpiredError):
        service.decode_token(token.value)


def test_decode_random_token_raises_invalid_error(service: JwtTokenService):
    with pytest.raises(TokenInvalidError):
        service.decode_token("random")