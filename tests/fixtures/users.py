import pytest

from shortener.domain.user import User
from shortener.domain.user.fields import Email, Name, HashedPassword


@pytest.fixture
def normal_user():
    return User(
        email=Email("normal.user@example.com"),
        name=Name("Normal User Example"),
        hashed_password=HashedPassword("hash")
    )
