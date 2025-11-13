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


@pytest.mark.parametrize(
    ("plain", "hashed", "expected_result"),
    [
        ("123", "123", False),
        ("123", PasslibPasswordHasher().hash("123"), True),
        ("1234", PasslibPasswordHasher().hash("123"), False),
        ("my@security#pass%123", PasslibPasswordHasher().hash("my@security#pass%123"), True),
    ]
)
def test_method_verify(
    password_hasher: PasslibPasswordHasher,
    plain: str,
    hashed: str,
    expected_result: bool
):
    assert password_hasher.verify(plain, hashed) == expected_result
