import pytest

from datetime import datetime

from shortener.domain.shared.datetime_utils import utc_now

from shortener.domain.plan import Plan

from shortener.domain.user import User
from shortener.domain.user.fields import Name, Email, HashedPassword, UserStatus
from tests.utils.date_helpers import assert_datetime


@pytest.fixture
def user(default_plan):
    return User(
        name=Name("User Example"),
        email=Email("user@gmail.com"),
        hashed_password=HashedPassword("hash#123"),
        plan=default_plan
    )


def test_pk(user: User):
    assert user.pk.is_undefined()


def test_name(user: User):
    assert user.name == "User Example"


def test_email(user: User):
    assert user.email == "user@gmail.com"


def test_hashed_password(user: User):
    assert user.hashed_password == "hash#123"


def test_plan(user: User):
    assert isinstance(user.plan, Plan)


def test_status(user: User):
    assert user.status == UserStatus.ACTIVE


def test_is_superuser(user: User):
    assert user.is_superuser == False


def test_created_at(user: User):
    created_at = user.created_at
    assert isinstance(created_at, datetime)

    now = utc_now()

    assert_datetime(
        created_at, now,
        year=True, month=True, day=True, hour=True, minute=True, second=True
    )


def test_last_login(user: User):
    assert user.last_login == None
