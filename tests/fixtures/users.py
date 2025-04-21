import pytest

from datetime import datetime, timezone

from shortener.domain.plan import Plan

from shortener.domain.user import User
from shortener.domain.user.fields import Email, Name, HashedPassword


@pytest.fixture
def normal_user(default_plan: Plan):
    return User(
        email=Email("normal.user@example.com"),
        name=Name("Normal User Example"),
        hashed_password=HashedPassword("hash"),
        plan=default_plan
    )


@pytest.fixture
def super_user(default_plan: Plan):
    return User(
        email=Email("i-love-superman@super.io"),
        name=Name("I Am Superman"),
        hashed_password=HashedPassword("superhash"),
        plan=default_plan
    )


@pytest.fixture
def old_user(default_plan: Plan):
    return User(
        email=Email("wiseoldman@example.com"),
        name=Name("Richard Park"),
        hashed_password=HashedPassword("2000"),
        plan=default_plan,
        created_at=datetime(year=2000, month=1, day=1, tzinfo=timezone.utc)
    )
