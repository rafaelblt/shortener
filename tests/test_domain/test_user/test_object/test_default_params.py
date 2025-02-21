from datetime import datetime, timezone

from shortener.domain.user import User

from pytest import fixture


@fixture
def user():
    return User(
        name="User Example",
        email="user@example.com",
        hashed_password="hash#123"
    )


def test_id(user):
    assert user.id == None


def test_name(user):
    assert user.name == "User Example"


def test_email(user):
    assert user.email == "user@example.com"


def test_hashed_password(user):
    assert user.hashed_password == "hash#123"


def test_is_active(user):
    assert user.is_active == True


def test_created_at(user):
    created_at = user.created_at
    now = datetime.now(tz=timezone.utc)

    assert isinstance(created_at, datetime)
    assert created_at.year == now.year
    assert created_at.month == now.month
    assert created_at.day == now.day
    assert created_at.hour == now.hour


def test_is_superuser(user):
    assert user.is_superuser == False


def test_last_login(user):
    assert user.last_login == None
