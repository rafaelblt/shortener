import pytest

from shortener.domain.services.password_hasher import PasswordHasherService

from tests.fixtures.mocks import MockPasswordHasherService


@pytest.fixture
def hasher(mock_password_hasher):
    return mock_password_hasher


def test_inheritance(hasher: MockPasswordHasherService):
    assert isinstance(hasher, PasswordHasherService)


def test_hash(hasher: MockPasswordHasherService):
    plain_password = "123"
    hashed = hasher.hash(plain_password)
    assert hashed == f"hashed-{plain_password}"


def test_verify(hasher: MockPasswordHasherService):
    plain_password = "123"
    hashed = hasher.hash(plain_password)
    assert hasher.verify(plain_password, hashed)