from datetime import timedelta
from typing import TypedDict

from shortener.domain.refresh_token import RefreshToken, RefreshTokenRepository

from shortener.domain.user import UserRepository
from shortener.domain.user.fields import Email
from shortener.domain.user.exceptions import (
    UserPasswordIncorrectError,
    UserNotFoundError
)

from shortener.domain.services.password_hasher import PasswordHasherService
from shortener.domain.services.token import TokenService, RandomTokenGenerator

from shortener.domain.shared.datetime_utils import utc_now
from shortener.domain.shared.primarykey import PrimaryKey
from shortener.domain.user.user import User


class LoginReturnType(TypedDict):
    access_token: str
    refresh_token: RefreshToken
    user: User


class LoginUserUseCase:
    def __init__(
        self,
        user_repository: UserRepository,
        refresh_token_repository: RefreshTokenRepository,
        password_hasher: PasswordHasherService,
        access_token_service: TokenService,
        access_token_expires_in: timedelta,
        refresh_token_generator: RandomTokenGenerator,
        refresh_token_expires_in: timedelta
    ):
        self.user_repository = user_repository
        self.refresh_token_repository = refresh_token_repository
        self.password_hasher = password_hasher
        self.access_token_service = access_token_service
        self.access_token_expires_in = access_token_expires_in
        self.refresh_token_generator = refresh_token_generator
        self.refresh_token_expires_in = refresh_token_expires_in

    async def execute(self, email: Email, password: str) -> LoginReturnType:
        """
        Executes the use case to login a user with the provided data.

        Args:
            email (Email): The user email.
            password (str): The user password.
        
        Returns:
            dict[str]: A dict with keys "access_token", "refresh_token" and "user".
        
        Raises:
            UserNotFoundError: If the email doesn't exist in database.
            UserEmailNotVerifiedError: The email has not been verified.
            UserSuspendedError: The user has been suspended.
            UserLockedError: The user has been locked.
            UserBannedError: The user has been banned.
            UserPasswordIncorrectError: If the password doesn't match.
        """
        user = await self.user_repository.get_by_email(email)
        if user is None:
            raise UserNotFoundError(value=email, field="email")

        password_match = self.password_hasher.verify(
            plain_password=password, hashed_password=user.hashed_password
        )
        if not password_match:
            raise UserPasswordIncorrectError()
        
        user.ensure_can_login()
        
        access_token = self.access_token_service.generate_token(
            subject=user.email,
            purpose=TokenService.Purpose.LOGIN,
            expires_in=self.access_token_expires_in,
        )

        refresh_token = RefreshToken(
            pk=PrimaryKey.create_pk_undefined(),
            token=self.refresh_token_generator.generate_token(),
            user=user,
            expires_at=utc_now() + self.refresh_token_expires_in
        )
        await self.refresh_token_repository.add(refresh_token)

        user.update_last_login()
        user = await self.user_repository.update(user)

        return LoginReturnType(
            access_token=access_token,
            refresh_token=refresh_token,
            user=user
        )
