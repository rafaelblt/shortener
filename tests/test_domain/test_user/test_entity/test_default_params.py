import pytest

from datetime import datetime, timezone

from shortener.domain.user import User
from shortener.domain.user.fields import Name, Email, HashedPassword, UserStatus


@pytest.fixture
def user():
    return User(
        name=Name("User Example"),
        email=Email("user@example.com"),
        hashed_password=HashedPassword("hash#123")
    )


def test_id(user):
    assert user.id == None


def test_name(user):
    assert user.name == "User Example"


def test_email(user):
    assert user.email == "user@example.com"


def test_hashed_password(user):
    assert user.hashed_password == "hash#123"


def test_status(user):
    assert user.status == UserStatus.ACTIVE


def test_shorturls(user):
    assert user.shorturls == []


def test_created_at(user):
    created_at = user.created_at
    assert isinstance(created_at, datetime)

    now = datetime.now(tz=timezone.utc)
    timeformat = "%d/%m/%Y %H:%M:%S"

    assert created_at.strftime(timeformat) == now.strftime(timeformat)


def test_is_superuser(user):
    assert user.is_superuser == False


def test_last_login(user):
    assert user.last_login == None
