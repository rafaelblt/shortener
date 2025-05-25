from abc import ABC, abstractmethod


class AuthTokenService(ABC):
    """Service for generating and decoding authentication tokens."""
    expires_minutes: int

    @abstractmethod
    def generate_token(self, subject: str) -> str:
        """
        Generates a token for the given subject.

        Args:
            subject (str): The subject (e.g., user identifier) for whom the 
                token is generated.

        Returns:
            str: The generated token.
        """
        pass

    @abstractmethod
    def decode_token(self, token: str) -> str:
        """
        Decodes the given token and returns the subject.

        Args:
            token (str): The token to decode.

        Returns:
            str: The subject extracted from the token.

        Raises:
            AuthTokenInvalidError: The token is invalid.
            AuthTokenExpiredError: The token is expired.
        """
        pass
