import pytest

from shortener.domain.shared.email import Email
from shortener.domain.shared.exceptions import EmailInvalidError


@pytest.mark.parametrize("email", [
    "user@hotmail.com",
    "user.name+tag+sorting@example.co.uk",
    "user_name@outlook.com",
    "user-name@gmail.com",
    "user123@google.com",
    "user@mail.com",
    "user@yahoo.com",
])
def test_valid_emails(email):
    assert Email.validate_email(email) is None


@pytest.mark.parametrize("email", [
    "",  
    "plainaddress",
    "@missinglocal.org",
    "user@.nodomain",
    "user@domain..com",
    "user@domain.com.",
    "user@-domain.com",
    "user@domain_com", 
    "user@.com",
    "user@domain..com",
    "user@domain..sub.com",
    "user@domain.c",  
])
def test_invalid_emails(email):
    with pytest.raises(
        EmailInvalidError, match=f"The provided email '{email}' is invalid."
    ):
        Email.validate_email(email)
