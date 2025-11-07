import asyncio

from typing import TypedDict

from shortener.domain.services.token import AuthTokenService, Token
from shortener.domain.user.user import User


class RefreshLoginReturnType(TypedDict):
    access_token: Token
    refresh_token: Token
    user: User


class RefreshLoginUseCase:
    def __init__(
        self,
        access_token_service: AuthTokenService,
        refresh_token_service: AuthTokenService,
    ):
        self.access_token_service = access_token_service
        self.refresh_token_service = refresh_token_service

    async def execute(self, token: str) -> RefreshLoginReturnType:
        """
        Consumes the provided token and generates a new access token and a new
        refresh token.

        Args:
            token(str): The token of RefreshToken.

        Returns:
            dict[str]: A dict with keys "access_token", "refresh_token" and "user".

        Raises:
            TokenInvalidError: The token is invalid.
            TokenExpiredError: The token is expired.
            UserEmailNotVerifiedError: The user email has not been verified.
            UserSuspendedError: The user of token has been suspended.
            UserLockedError: The user of token has been locked.
            UserBannedError: The user of token has been banned.
        """
        user = await self.refresh_token_service.decode_token(token)
        user.ensure_can_login()
        access_token, refresh_token = await asyncio.gather(
            self.access_token_service.generate_token(user),
            self.refresh_token_service.generate_token(user)
        )
        return RefreshLoginReturnType(
            access_token=access_token,
            refresh_token=refresh_token,
            user=user
        )
