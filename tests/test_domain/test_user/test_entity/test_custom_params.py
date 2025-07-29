import pytest

from datetime import datetime, timezone

from shortener.domain.plan import Plan

from shortener.domain.shared.primarykey import PrimaryKey
from shortener.domain.user import User
from shortener.domain.user.fields import Name, Email, HashedPassword, UserStatus
from tests.utils.date_helpers import assert_datetime


@pytest.fixture
def user(default_plan):
    return User(
        pk=PrimaryKey.create_pk_id(15),
        name=Name("User Name Test Example"),
        email=Email("user-user@outlook.com"),
        hashed_password=HashedPassword("hash#@$%12356788"),
        plan=default_plan,
        status=UserStatus.BANNED,
        is_superuser=True,
        created_at=datetime(year=2010, month=5, day=22, tzinfo=timezone.utc),
        last_login=datetime(year=2010, month=5, day=25, tzinfo=timezone.utc)
    )


def test_id(user: User):
    assert user.pk.get_id() == 15


def test_name(user: User):
    assert user.name == "User Name Test Example"


def test_email(user: User):
    assert user.email == "user-user@outlook.com"


def test_hashed_password(user: User):
    assert user.hashed_password == "hash#@$%12356788"


def test_plan(user: User):
    assert isinstance(user.plan, Plan)


def test_status(user: User):
    assert user.status == UserStatus.BANNED


def test_is_superuser(user: User):
    assert user.is_superuser == True


def test_created_at(user: User):
    created_at = user.created_at
    assert isinstance(created_at, datetime)

    expected = datetime(year=2010, month=5, day=22, tzinfo=timezone.utc)

    assert_datetime(
        created_at, expected,
        year=True, month=True, day=True
    )


def test_last_login(user: User):
    last_login = user.last_login
    assert isinstance(last_login, datetime)

    expected = datetime(year=2010, month=5, day=25, tzinfo=timezone.utc)

    assert_datetime(
        last_login, expected,
        year=True, month=True, day=True
    )
