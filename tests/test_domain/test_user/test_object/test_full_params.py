from datetime import datetime, timezone

from shortener.domain.user import User

from pytest import fixture


@fixture
def user():
    return User(
        id=15,
        name="User Test Example",
        email="user-user@example.com",
        hashed_password="hash#@$%12356788",
        is_active=False,
        is_superuser=True,
        created_at=datetime(year=2010, month=5, day=22),
        last_login=datetime(year=2010, month=5, day=25)
    )


def test_id(user):
    assert user.id == 15


def test_name(user):
    assert user.name == "User Test Example"


def test_email(user):
    assert user.email == "user-user@example.com"


def test_hashed_password(user):
    assert user.hashed_password == "hash#@$%12356788"


def test_is_active(user):
    assert user.is_active == False


def test_created_at(user):
    created_at = user.created_at
    expected = datetime(year=2010, month=5, day=22)

    assert isinstance(created_at, datetime)
    assert created_at.year == expected.year
    assert created_at.month == expected.month
    assert created_at.day == expected.day
    assert created_at.hour == expected.hour


def test_is_superuser(user):
    assert user.is_superuser == True


def test_last_login(user):
    last_login = user.last_login
    expected = datetime(year=2010, month=5, day=25)

    assert isinstance(last_login, datetime)
    assert last_login.year == expected.year
    assert last_login.month == expected.month
    assert last_login.day == expected.day
    assert last_login.hour == expected.hour
