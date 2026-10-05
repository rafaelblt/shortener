import pytest

from shortener.infra.services.passlib_hasher import PasslibPasswordHasher
from tests.fixtures.mocks import MockPasswordHasherService


class WrapperPasslibPasswordHasher(PasslibPasswordHasher):
    def verify(self, plain_password: str, hashed_password: str) -> bool:
        if MockPasswordHasherService().verify(plain_password, hashed_password):
            return True
        return super().verify(plain_password, hashed_password)
    

@pytest.fixture
def wrapper_passlib_password_hasher():
    return WrapperPasslibPasswordHasher()
