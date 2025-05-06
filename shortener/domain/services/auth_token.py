from abc import ABC, abstractmethod


class AuthTokenService(ABC):

    @abstractmethod
    def generate_token(self, subject: str) -> str:
        pass

    @abstractmethod
    def decode_token(self, token: str) -> str:
        """
        

        Args:
            token (str): The auth token.

        Returns:
            str

        Raises:
            AuthTokenInvalidError: The token is invalid.
            AuthTokenExpiredError: The token is expired.
        """
        pass
