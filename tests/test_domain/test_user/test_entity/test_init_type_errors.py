import pytest

from datetime import datetime

from shortener.domain.user import User
from shortener.domain.user.fields import Name, Email, HashedPassword


@pytest.fixture
def valid_name():
    return Name("Example Name Stone")

@pytest.fixture
def valid_email():
    return Email("test-email@example.com")

@pytest.fixture
def valid_hashed_password():
    return HashedPassword("AD@34m1~d/a@@f#kl2$$6@5$61*1")

@pytest.fixture
def required_fields(valid_email, valid_name, valid_hashed_password):
    return {
        "email": valid_email,
        "name": valid_name,
        "hashed_password": valid_hashed_password
    }


def get_type_error_message(attr, type_expected, got):
    return (
        f"The User {attr} must be an instance of {type_expected}, got "
        f"{type(got).__name__}"
    )


def test_invalid_id(valid_email, valid_name, valid_hashed_password):
    invalid_id = "1"
    with pytest.raises(
        TypeError, 
        match=get_type_error_message(
            attr="id", type_expected="int or None", got=invalid_id
        )
    ):
        User(
            email=valid_email, 
            hashed_password=valid_hashed_password, 
            name=valid_name, 
            id=invalid_id
        )


def test_invalid_name(valid_email, valid_hashed_password):
    invalid_name = None
    with pytest.raises(
        TypeError, 
        match=get_type_error_message(
            attr="name", type_expected="Name", got=invalid_name
        )
    ):
        User(
            name=invalid_name, 
            email=valid_email, 
            hashed_password=valid_hashed_password
        )


def test_invalid_email(valid_name, valid_hashed_password):
    invalid_email = None
    with pytest.raises(
        TypeError, 
        match=get_type_error_message(
            attr="email", type_expected="Email", got=invalid_email
        )
    ):
        User(
            name=valid_name,
            email=invalid_email,
            hashed_password=valid_hashed_password
        )


def test_invalid_hashed_password(valid_name, valid_email):
    invalid_hashed_password = None
    with pytest.raises(
        TypeError, 
        match=get_type_error_message(
            attr="hashed_password", 
            type_expected="HashedPassword", 
            got=invalid_hashed_password
        )
    ):
        User(
            email=valid_email,
            name=valid_name,
            hashed_password=invalid_hashed_password
        )


def test_invalid_shorturls(required_fields):
    invalid_shorturls = None
    with pytest.raises(
        TypeError, 
        match=get_type_error_message(
            attr="shorturls", type_expected="list", got=invalid_shorturls
        )
    ):
        User(**required_fields, shorturls=invalid_shorturls)


def test_shorturls_with_non_shorturls(required_fields):
    invalid_shorturls = [1, "a", True]
    with pytest.raises(
        TypeError, 
        match="The User shorturls must be a list of only ShortURLs."
    ):
        User(**required_fields, shorturls=invalid_shorturls)


def test_invalid_status(required_fields):
    invalid_status = None
    with pytest.raises(
        TypeError, 
        match=get_type_error_message(
            attr="status", type_expected="UserStatus", got=invalid_status
        )
    ):
        User(**required_fields, status=invalid_status)


def test_invalid_is_superuser(required_fields):
    invalid_is_superuser = None
    with pytest.raises(
        TypeError, 
        match=get_type_error_message(
            attr="is_superuser", type_expected="bool", got=invalid_is_superuser
        )
    ):
        User(**required_fields, is_superuser=invalid_is_superuser)


def test_invalid_created_at(required_fields):
    invalid_created_at = True
    with pytest.raises(
        TypeError, 
        match=get_type_error_message(
            attr="created_at", type_expected="datetime", got=invalid_created_at
        )
    ):
        User(**required_fields, created_at=invalid_created_at)


def test_invalid_created_at_timezone(required_fields):
    invalid_created_at = datetime(1, 2, 3)
    with pytest.raises(
        ValueError, 
        match="The User created_at datetime must be in UTC timezone."
    ):
        User(**required_fields, created_at=invalid_created_at)


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
        User(**required_fields, last_login=invalid_last_login)


def test_invalid_last_login_timezone(required_fields):
    invalid_last_login = datetime(1, 2, 3)
    with pytest.raises(
        ValueError, 
        match="The User last_login datetime must be in UTC timezone."
    ):
        User(**required_fields, last_login=invalid_last_login)
