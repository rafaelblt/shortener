from shortener.domain.services.password_hasher import PasswordHasherService


class MockPasswordHasherService(PasswordHasherService):
    def hash(self, plain_password: str) -> str:
        return f"hashed-{plain_password}"

    def verify(self, plain_password: str, hashed_password: str) -> bool:
        return hashed_password == f"hashed-{plain_password}"
