import pytest

from datetime import timedelta

from shortener.domain.services.token import Token, TokenService, TokenInvalidError, TokenExpiredError
from shortener.domain.shared.datetime_utils import utc_now

from tests.fixtures.mocks import MockTokenService


@pytest.fixture
def service(mock_token_service):
    return mock_token_service


def test_inheritance(service: MockTokenService):
    assert isinstance(service, TokenService)


def test_singleton(service: MockTokenService):
    other_instance = MockTokenService()
    assert other_instance == service


def test_generate_token(service: MockTokenService):
    subject = "user123"
    purpose = "purpose123"
    expires_in = timedelta(minutes=1)

    token = service.generate_token(
        subject=subject,
        purpose=purpose,
        expires_in=expires_in
    )

    assert isinstance(token, Token)

    mock_token = service.mock_data["generated_tokens"][0]
    assert mock_token["token"] == token.value
    assert mock_token["subject"] == subject
    assert mock_token["purpose"] == purpose
    assert mock_token["secret_key"] == service._secret_key
    assert mock_token["expires_at"] == mock_token["created_at"] + expires_in
    assert (
        mock_token["created_at"].replace(microsecond=0) ==
        utc_now().replace(microsecond=0)
    )


def test_decode_token(service: MockTokenService):
    subject = "user123"
    purpose = "purpose123"
    expires_in = timedelta(minutes=1)

    token = service.generate_token(
        subject=subject,
        purpose=purpose,
        expires_in=expires_in
    )

    decoded = service.decode_token(token.value)    
    
    assert decoded["subject"] == subject
    assert decoded["purpose"] == purpose
    assert decoded["created_at"] == token.created_at
    assert decoded["expires_at"] == token.expires_at
    assert decoded["extra_claims"] == token.extra_claims


def test_decode_token_raises_invalid_error(service: MockTokenService):
    with pytest.raises(TokenInvalidError):
        service.decode_token("invalid")


def test_decode_token_raises_expired_error(service: MockTokenService):
    subject = "user123"
    purpose = "pyroise"
    expires_in = timedelta(microseconds=1)

    token = service.generate_token(
        subject=subject,
        purpose=purpose,
        expires_in=expires_in
    )

    with pytest.raises(TokenExpiredError):
        service.decode_token(token.value)


def test_mock_data(service: MockTokenService):
    assert len(service.mock_data["generated_tokens"]) == 0

    subject = "user123"
    purpose = "purpose123"
    expires_in = timedelta(minutes=1)

    token = service.generate_token(
        subject=subject,
        purpose=purpose,
        expires_in=expires_in
    )
    
    assert len(service.mock_data["generated_tokens"]) == 1
    assert service.mock_data["generated_tokens"][0]["token"] == token.value
