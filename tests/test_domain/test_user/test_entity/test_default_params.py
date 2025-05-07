import pytest

from datetime import datetime

from shortener.domain.shared.datetime_utils import utc_now

from shortener.domain.plan import Plan

from shortener.domain.user import User
from shortener.domain.user.fields import Name, Email, HashedPassword, UserStatus


@pytest.fixture
def user(default_plan):
    return User(
        name=Name("User Example"),
        email=Email("user@gmail.com"),
        hashed_password=HashedPassword("hash#123"),
        plan=default_plan
    )


def test_id(user):
    assert user.id == None


def test_name(user):
    assert user.name == "User Example"


def test_email(user):
    assert user.email == "user@gmail.com"


def test_hashed_password(user):
    assert user.hashed_password == "hash#123"


def test_plan(user):
    assert isinstance(user.plan, Plan)


def test_shorturls_count(user):
    assert user.shorturls_count == 0


def test_status(user):
    assert user.status == UserStatus.ACTIVE


def test_is_superuser(user):
    assert user.is_superuser == False


def test_created_at(user):
    created_at = user.created_at
    assert isinstance(created_at, datetime)

    now = utc_now()
    timeformat = "%d/%m/%Y %H:%M:%S"

    assert created_at.strftime(timeformat) == now.strftime(timeformat)


def test_last_login(user):
    assert user.last_login == None
