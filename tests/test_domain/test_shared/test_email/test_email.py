import pytest
from shortener.domain.shared.email import Email
from shortener.domain.shared.exceptions import EmailInvalidError


def test_new_email():
    email = Email("test-email@outlook.com")
    assert isinstance(email, Email)
    assert isinstance(email, str)
    assert email == "test-email@outlook.com"


def test_email_repr():
    email = Email("google.user@gmail.com")
    assert email.__repr__() == f"<Email 'google.user@gmail.com'>"


def test_new_email_raises_type_error():
    with pytest.raises(TypeError, match="Email value arg must be a str."):
        Email(1) # type: ignore


def test_new_email_raises_validation_error():
    value = "12"
    with pytest.raises(EmailInvalidError):
        Email(value)
