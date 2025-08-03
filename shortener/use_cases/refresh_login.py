from typing import TypedDict
from datetime import timedelta

from shortener.domain.refresh_token import RefreshToken, RefreshTokenRepository
from shortener.domain.refresh_token.exceptions import RefreshTokenNotFoundError

from shortener.domain.services.token import TokenService, RandomTokenGenerator

from shortener.domain.shared.datetime_utils import utc_now
from shortener.domain.shared.primarykey import PrimaryKey
from shortener.domain.user.user import User


class RefreshLoginReturnType(TypedDict):
    access_token: str
    refresh_token: RefreshToken
    user: User


class RefreshLoginUseCase:
    def __init__(
        self,
        refresh_token_repository: RefreshTokenRepository,
        access_token_service: TokenService,
        access_token_expires_in: timedelta,
        refresh_token_generator: RandomTokenGenerator,
        refresh_token_expires_in: timedelta
    ):
        self.refresh_token_repository = refresh_token_repository
        self.access_token_service = access_token_service
        self.access_token_expires_in = access_token_expires_in
        self.refresh_token_generator = refresh_token_generator
        self.refresh_token_expires_in = refresh_token_expires_in

    async def execute(self, refresh_token: str) -> RefreshLoginReturnType:
        """
        Consumes the provided token and generates a new access token and a new
        refresh token.

        Args:
            refresh_token(str): The token of RefreshToken.

        Returns:
            dict[str]: A dict with keys "access_token", "refresh_token" and "user".

        Raises:
            RefreshTokenNotFoundError: The token is not found.
            RefreshTokenRevokedError: The token is revoked.
            RefreshTokenExpiredError: The token is expired.
            UserEmailNotVerifiedError: The user has not been verified.
            UserSuspendedError: The user has been suspended.
            UserLockedError: The user has been locked.
            UserBannedError: The user has been banned.
        """
        token = await self.refresh_token_repository.get_by_token(refresh_token)
        if token is None:
            raise RefreshTokenNotFoundError(value=refresh_token, field="token")

        token.consume()

        access_token = self.access_token_service.generate_token(
            subject=token.user.email,
            purpose=TokenService.Purpose.LOGIN,
            expires_in=self.access_token_expires_in,
        )

        new_refresh_token = RefreshToken(
            pk=PrimaryKey.create_pk_undefined(),
            token=self.refresh_token_generator.generate_token(),
            user=token.user,
            expires_at=utc_now() + self.refresh_token_expires_in
        )

        new_refresh_token = await self.refresh_token_repository.add(new_refresh_token)
        await self.refresh_token_repository.update(token)

        return RefreshLoginReturnType(
            access_token=access_token,
            refresh_token=new_refresh_token,
            user=token.user
        )
