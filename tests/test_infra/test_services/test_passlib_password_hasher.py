import pytest

from passlib.context import CryptContext

from shortener.domain.user.fields.hashed_password import HashedPassword
from shortener.infra.services.passlib_hasher import PasslibPasswordHasher


@pytest.fixture
def password_hasher():
    return PasslibPasswordHasher()


def test_attr_pwd_context(password_hasher: PasslibPasswordHasher):
    assert hasattr(password_hasher, "pwd_context")
    assert isinstance(password_hasher.pwd_context, CryptContext)


def test_method_hash(password_hasher: PasslibPasswordHasher):
    pw = "mypass123"
    retrieved = password_hasher.hash(pw)
    assert isinstance(retrieved, HashedPassword)
    assert str(retrieved) != pw


def test_method_verify(password_hasher: PasslibPasswordHasher):
    plain = "my@security#pass%123"
    hashed = password_hasher.hash(plain)
    
    assert password_hasher.verify(plain, hashed)
    assert password_hasher.verify("other_password", hashed) is False
