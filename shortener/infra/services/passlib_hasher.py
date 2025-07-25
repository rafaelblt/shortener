from shortener.domain.services.password_hasher import PasswordHasherService

from passlib.context import CryptContext

from shortener.domain.user.fields.hashed_password import HashedPassword


class PasslibPasswordHasher(PasswordHasherService):
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def hash(self, plain_password: str) -> HashedPassword:
        return HashedPassword(self.pwd_context.hash(plain_password))

    def verify(self, plain_password: str, hashed_password: str) -> bool:
        return self.pwd_context.verify(plain_password, hashed_password)
