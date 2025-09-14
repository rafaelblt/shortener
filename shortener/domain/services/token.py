from abc import ABC, abstractmethod
from datetime import timedelta
from typing import Any, Mapping

from shortener.domain.user import User
from shortener.domain.services.exceptions import TokenInvalidError, TokenExpiredError

from shortener.domain.shared.token import Token, TokenDecoded


class TokenService(ABC):
    """Service for generating and decoding general-purpose tokens."""

    @abstractmethod
    def generate_token(
        self,
        subject: str,
        purpose: str,
        expires_in: timedelta,
        extra_claims: Mapping[str, Any] | None = None
    ) -> Token:
        """
        Generates a token for the given subject and purpose.

        Args:
            subject (str): The subject (e.g., user identifier or email).
            purpose (str): The purpose of the token (e.g., "login", "email-verification").
            expires_in (timedelta): The time duration until expiration.
            extra_claims (dict, optional): Any additional claims to embed.

        Returns:
            str: The generated token.
        """
        pass

    @abstractmethod
    def decode_token(self, token: str) -> TokenDecoded:
        """
        Decodes the given token and returns its payload.

        Args:
            token (str): The token to decode.

        Returns:
            dict: The payload extracted from the valid token.

        Raises:
            TokenInvalidError: The token is invalid.
            TokenExpiredError: The token is expired.
        """
        pass


class AuthTokenService(ABC):
    """Service for generating and decoding authentication tokens."""

    @abstractmethod
    async def generate_token(self, user: User) -> Token:
        """
        Generates a token for the given user.

        Args:
            user (User): The user for whom to generate the token.

        Returns:
            Token: The generated token.
        """
        pass

    @abstractmethod
    async def decode_token(self, token: str) -> User:
        """
        Decodes the given token and returns the User.

        Args:
            token (str): The token to decode.

        Returns:
            User: The user extracted from the token.

        Raises:
            TokenInvalidError: The token is invalid.
            TokenExpiredError: The token is expired.
        """
        pass
