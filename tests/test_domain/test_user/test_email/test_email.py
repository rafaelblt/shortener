import pytest
from shortener.domain.user.fields.email import Email
from shortener.domain.user.exceptions import UserEmailInvalidPatternError


def test_new_email():
    email = Email("test-email@example.com")
    assert isinstance(email, Email)
    assert isinstance(email, str)
    assert email == "test-email@example.com"


def test_email_repr():
    email = Email("google.user@gmail.com")
    assert email.__repr__() == f"<Email 'google.user@gmail.com'>"


def test_new_email_raises_type_error():
    with pytest.raises(TypeError, match="Email value arg must be a str."):
        Email(1)


def test_new_email_raises_validation_error():
    value = "12"
    with pytest.raises(UserEmailInvalidPatternError):
        Email(value)
