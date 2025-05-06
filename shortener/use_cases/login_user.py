from shortener.domain.services.password_hasher import PasswordHasher
from shortener.domain.services.auth_token import AuthTokenService

from shortener.domain.user import UserRepository
from shortener.domain.user.fields import Email
from shortener.domain.user.exceptions import (
    UserPasswordIncorretError,
    UserNotFoundInDatabaseError
)


class LoginUserUseCase:
    def __init__(
        self,
        repository: UserRepository,
        password_hasher: PasswordHasher,
        auth_token_service: AuthTokenService
    ):
        self.repository = repository
        self.password_hasher = password_hasher
        self.auth_token_service = auth_token_service

    async def execute(self, email: Email, password: str) -> str:
        """
        Executes the use case to login a user with the provided data.

        Args:
            email (Email): The user email.
            password (str): The user password.
        
        Returns:
            str: The auth token.
        
        Raises:
            UserNotFoundInDatabaseError: If the email doesn't exist in database.
            UserPasswordIncorrectError: If the password doesn't match.
        """
        user = await self.repository.get_by_email(email)
        if user is None:
            raise UserNotFoundInDatabaseError()

        password_match = self.password_hasher.verify(
            plain_password=password, hashed_password=user.hashed_password
        )
        if password_match:
            return self.auth_token_service.generate_token()
        raise UserPasswordIncorretError()
