import pytest

from datetime import datetime, timedelta, timezone

from shortener.domain.services.token import TokenService, TokenInvalidError, TokenExpiredError

from shortener.domain.shared.datetime_utils import utc_now
from tests.fixtures import MockTokenService


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
    purpose = service.Purpose.EMAIL_VERIFICATION
    expires_in = timedelta(minutes=1)

    token = service.generate_token(
        subject=subject,
        purpose=purpose,
        expires_in=expires_in
    )

    assert isinstance(token, str)

    token_split = token.split("|")
    assert len(token_split) == 4
    assert token_split[0] == subject
    assert token_split[1] == purpose.value
    assert token_split[2] == service._secret_key

    timeformat = "%d/%m/%Y %H:%M:%S"
    retrieved_expiration = datetime.fromtimestamp(
        float(token_split[3]), tz=timezone.utc
    )
    expected_expiration = utc_now() + expires_in
    assert (
        retrieved_expiration.strftime(timeformat) ==
        expected_expiration.strftime(timeformat)
    )


def test_decode_token(service: MockTokenService):
    subject = "user123"
    purpose = service.Purpose.EMAIL_VERIFICATION
    expires_in = timedelta(minutes=1)

    token = service.generate_token(
        subject=subject,
        purpose=purpose,
        expires_in=expires_in
    )

    payload = service.decode_token(token)
    
    
    assert payload["subject"] == subject
    assert payload["purpose"] == purpose.value


def test_decode_token_raises_invalid_error(service: MockTokenService):
    subject = "user123"
    purpose = service.Purpose.EMAIL_VERIFICATION
    expires_in = timedelta(minutes=1)

    token = service.generate_token(
        subject=subject,
        purpose=purpose,
        expires_in=expires_in
    )
    
    with pytest.raises(TokenInvalidError):
        invalid_token_format = str(token.split("|"))
        service.decode_token(invalid_token_format)
    with pytest.raises(TokenInvalidError):
        token_split = token.split("|")
        token_split[2] = "new_secret_key"
        invalid_token_key = "|".join(token_split)
        service.decode_token(invalid_token_key)


def test_decode_token_raises_expired_error(service: MockTokenService):
    subject = "user123"
    purpose = service.Purpose.EMAIL_VERIFICATION
    expires_in = timedelta(microseconds=1)

    token = service.generate_token(
        subject=subject,
        purpose=purpose,
        expires_in=expires_in
    )

    with pytest.raises(TokenExpiredError):
        service.decode_token(token)


def test_mock_data(service: MockTokenService):
    assert len(service.mock_data["generated_tokens"]) == 0

    subject = "user123"
    purpose = service.Purpose.EMAIL_VERIFICATION
    expires_in = timedelta(minutes=1)

    token = service.generate_token(
        subject=subject,
        purpose=purpose,
        expires_in=expires_in
    )
    
    assert len(service.mock_data["generated_tokens"]) == 1
    assert service.mock_data["generated_tokens"][0] == token
