from abc import ABC, abstractmethod
from datetime import timedelta
from enum import Enum
from typing import Any, Mapping, TypedDict, Optional


class Payload(TypedDict):
    subject: str
    purpose: str
    expires_in: timedelta
    extra_claims: Optional[Mapping[str, Any]]


class TokenService(ABC):
    """Service for generating and decoding general-purpose tokens."""

    class Purpose(str, Enum):
        EMAIL_VERIFICATION = "email_verification"

    @abstractmethod
    def generate_token(
        self,
        subject: str,
        purpose: str,
        expires_in: timedelta,
        extra_claims: Mapping[str, Any] | None = None
    ) -> str:
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
    def decode_token(self, token: str) -> Payload:
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
