from abc import ABC, abstractmethod


class AuthTokenService(ABC):

    @abstractmethod
    def generate_token(self, subject: str) -> str:
        pass

    @abstractmethod
    def decode_token(self, token: str) -> str | None:
        pass
