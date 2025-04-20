import pytest

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
