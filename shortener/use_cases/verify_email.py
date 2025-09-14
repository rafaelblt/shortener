from shortener.domain.user.exceptions import UserNotFoundError

from shortener.domain.services.token import AuthTokenService, TokenInvalidError

from shortener.domain.user import UserRepository


class VerifyEmailUseCase:
    """Use Case to verify a user's email address."""

    def __init__(
        self,
        user_repository: UserRepository,
        token_service: AuthTokenService
    ):
        self.user_repository = user_repository
        self.token_service = token_service
    
    async def execute(self, token: str):
        """
        Verifies the user's email using the provided token.

        Args:
            token (str): The verification token.
        
        Returns:
            None: The user is verified.

        Raises:
            TokenInvalidError: The token is invalid.
            TokenExpiredError: The token is expired.
            UserNotFoundError: If the user is not found in the database.
            UserStatusInvalidToVerifyEmailError: If the user status is not 
                UNVERIFIED_EMAIL.
        """
        user = await self.token_service.decode_token(token)
        user.verify_email()
        await self.user_repository.update(user)
