import pytest

from datetime import datetime, timezone

from shortener.domain.plan import Plan

from shortener.domain.user import User
from shortener.domain.user.fields import Email, Name, HashedPassword, UserStatus


@pytest.fixture
def normal_user(default_plan: Plan):
    return User(
        email=Email("normal.user@gmail.com"),
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
        email=Email("wiseoldman@outlook.com"),
        name=Name("Richard Park"),
        hashed_password=HashedPassword("2000"),
        plan=default_plan,
        created_at=datetime(year=2000, month=1, day=1, tzinfo=timezone.utc)
    )


@pytest.fixture
def unverified_email_user(default_plan: Plan):
    return User(
        email=Email("i-was-not-checked@gmail.com"),
        name=Name("Unverified Person"),
        hashed_password=HashedPassword("n0t"),
        plan=default_plan,
        status=UserStatus.UNVERIFIED_EMAIL
    )


@pytest.fixture
def banned_user(default_plan: Plan):
    return User(
        email=Email("i-was-banned@gmail.com"),
        name=Name("Banned Person"),
        hashed_password=HashedPassword("banpass123"),
        plan=default_plan,
        status=UserStatus.BANNED
    )


@pytest.fixture
def suspended_user(default_plan: Plan):
    return User(
        email=Email("i-was-suspended@gmail.com"),
        name=Name("Suspended Person"),
        hashed_password=HashedPassword("sus"),
        plan=default_plan,
        status=UserStatus.SUSPENDED
    )


@pytest.fixture
def locked_user(default_plan: Plan):
    return User(
        email=Email("i-was-locked@gmail.com"),
        name=Name("Locked Person"),
        hashed_password=HashedPassword("belocked"),
        plan=default_plan,
        status=UserStatus.LOCKED
    )
