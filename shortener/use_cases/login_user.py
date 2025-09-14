import asyncio

from typing import TypedDict

from shortener.domain.user import UserRepository
from shortener.domain.user.fields import Email
from shortener.domain.user.exceptions import (
    UserPasswordIncorrectError,
    UserNotFoundError
)

from shortener.domain.services.password_hasher import PasswordHasherService
from shortener.domain.services.token import Token, AuthTokenService

from shortener.domain.user.user import User


class LoginReturnType(TypedDict):
    access_token: Token
    refresh_token: Token
    user: User


class LoginUserUseCase:
    def __init__(
        self,
        user_repository: UserRepository,
        password_hasher: PasswordHasherService,
        access_token_service: AuthTokenService,
        refresh_token_service: AuthTokenService,
    ):
        self.user_repository = user_repository
        self.password_hasher = password_hasher
        self.access_token_service = access_token_service
        self.refresh_token_service = refresh_token_service

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
        
        access_token, refresh_token = await asyncio.gather(
            self.access_token_service.generate_token(user),
            self.refresh_token_service.generate_token(user)
        )

        user.update_last_login()
        user = await self.user_repository.update(user)

        return LoginReturnType(
            access_token=access_token,
            refresh_token=refresh_token,
            user=user
        )
