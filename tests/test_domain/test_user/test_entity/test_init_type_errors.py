import pytest

from datetime import datetime

from shortener.domain.user import User
from shortener.domain.user.fields import Name, Email, HashedPassword


@pytest.fixture
def required_fields(default_plan):
    return {
        "email": Email("test-email@gmail.com"),
        "name": Name("Example Name Stone"),
        "hashed_password": HashedPassword("AD@34m1~d/a@@f#kl2$$6@5$61*1"),
        "plan": default_plan
    }


def get_type_error_message(attr, type_expected, got):
    return (
        f"The User {attr} must be an instance of {type_expected}, got "
        f"{type(got).__name__}"
    )


def test_invalid_id(required_fields):
    invalid_pk = 1
    with pytest.raises(
        TypeError, 
        match=get_type_error_message(
            attr="id", type_expected="int or None", got=invalid_pk
        )
    ):
        User(**required_fields, pk=invalid_pk) # type: ignore


def test_invalid_name(required_fields):
    required_fields.pop("name")
    invalid_name = None
    with pytest.raises(
        TypeError, 
        match=get_type_error_message(
            attr="name", type_expected="Name", got=invalid_name
        )
    ):
        User(**required_fields, name=invalid_name) # type: ignore


def test_invalid_email(required_fields):
    required_fields.pop("email")
    invalid_email = None
    with pytest.raises(
        TypeError, 
        match=get_type_error_message(
            attr="email", type_expected="Email", got=invalid_email
        )
    ):
        User(**required_fields, email=invalid_email) # type: ignore


def test_invalid_hashed_password(required_fields):
    required_fields.pop("hashed_password")
    invalid_hashed_password = None
    with pytest.raises(
        TypeError, 
        match=get_type_error_message(
            attr="hashed_password", 
            type_expected="HashedPassword", 
            got=invalid_hashed_password
        )
    ):
        User(**required_fields, hashed_password=invalid_hashed_password) # type: ignore


def test_invalid_status(required_fields):
    invalid_status = None
    with pytest.raises(
        TypeError, 
        match=get_type_error_message(
            attr="status", type_expected="UserStatus", got=invalid_status
        )
    ):
        User(**required_fields, status=invalid_status) # type: ignore


def test_invalid_is_superuser(required_fields):
    invalid_is_superuser = None
    with pytest.raises(
        TypeError, 
        match=get_type_error_message(
            attr="is_superuser", type_expected="bool", got=invalid_is_superuser
        )
    ):
        User(**required_fields, is_superuser=invalid_is_superuser) # type: ignore


def test_invalid_created_at(required_fields):
    invalid_created_at = True
    with pytest.raises(
        TypeError, 
        match=get_type_error_message(
            attr="created_at", type_expected="datetime", got=invalid_created_at
        )
    ):
        User(**required_fields, created_at=invalid_created_at) # type: ignore


def test_invalid_created_at_timezone(required_fields):
    invalid_created_at = datetime(1, 2, 3)
    with pytest.raises(
        ValueError, 
        match="The User created_at datetime must be in UTC timezone."
    ):
        User(**required_fields, created_at=invalid_created_at) # type: ignore


def test_invalid_last_login(required_fields):
    invalid_last_login = "today"
    with pytest.raises(
        TypeError, 
        match=get_type_error_message(
            attr="last_login", 
            type_expected="datetime or None", 
            got=invalid_last_login
        )
    ):
        User(**required_fields, last_login=invalid_last_login) # type: ignore


def test_invalid_last_login_timezone(required_fields):
    invalid_last_login = datetime(1, 2, 3)
    with pytest.raises(
        ValueError, 
        match="The User last_login datetime must be in UTC timezone."
    ):
        User(**required_fields, last_login=invalid_last_login) # type: ignore
