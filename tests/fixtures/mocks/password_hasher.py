import pytest

from shortener.domain.services.password_hasher import PasswordHasherService

from shortener.domain.user.fields import HashedPassword


class MockPasswordHasherService(PasswordHasherService):
    def hash(self, plain_password: str) -> HashedPassword:
        return HashedPassword(f"hashed-{plain_password}")

    def verify(self, plain_password: str, hashed_password: str) -> bool:
        return hashed_password == f"hashed-{plain_password}"


@pytest.fixture
def mock_password_hasher():
    return MockPasswordHasherService()
