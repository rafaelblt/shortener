import pytest

from datetime import datetime, timezone

from shortener.domain.plan import Plan

from shortener.domain.user import User
from shortener.domain.user.fields import Name, Email, HashedPassword, UserStatus


@pytest.fixture
def user(default_plan):
    return User(
        id=15,
        name=Name("User Name Test Example"),
        email=Email("user-user@outlook.com"),
        hashed_password=HashedPassword("hash#@$%12356788"),
        plan=default_plan,
        shorturls_count=4,
        status=UserStatus.BANNED,
        is_superuser=True,
        created_at=datetime(year=2010, month=5, day=22, tzinfo=timezone.utc),
        last_login=datetime(year=2010, month=5, day=25, tzinfo=timezone.utc)
    )


def test_id(user):
    assert user.id == 15


def test_name(user):
    assert user.name == "User Name Test Example"


def test_email(user):
    assert user.email == "user-user@outlook.com"


def test_hashed_password(user):
    assert user.hashed_password == "hash#@$%12356788"


def test_plan(user):
    assert isinstance(user.plan, Plan)


def test_shorturls_count(user):
    assert user.shorturls_count == 4


def test_status(user):
    assert user.status == UserStatus.BANNED


def test_is_superuser(user):
    assert user.is_superuser == True


def test_created_at(user):
    created_at = user.created_at
    assert isinstance(created_at, datetime)

    expected = datetime(year=2010, month=5, day=22, tzinfo=timezone.utc)
    timeformat = "%d/%m/%Y %H:%M:%S"

    assert created_at.strftime(timeformat) == expected.strftime(timeformat)


def test_last_login(user):
    last_login = user.last_login
    assert isinstance(last_login, datetime)

    expected = datetime(year=2010, month=5, day=25, tzinfo=timezone.utc)
    timeformat = "%d/%m/%Y %H:%M:%S"

    assert last_login.strftime(timeformat) == expected.strftime(timeformat)
