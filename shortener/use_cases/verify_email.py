from shortener.domain.user.exceptions import UserNotFoundInDatabaseError

from shortener.domain.services.auth_token import AuthTokenService

from shortener.domain.user import UserRepository


class VerifyEmailUseCase:
    """Use Case to verify a user's email address."""

    def __init__(
        self,
        user_repository: UserRepository,
        auth_token_service: AuthTokenService
    ):
        """
        Args:
            user_repository: Repository to find and update the user.
            auth_token_service: Service to decode the verify token.
        """
        self.user_repository = user_repository
        self.auth_token_service = auth_token_service
    
    async def execute(self, token: str):
        """
        Verifies the user's email using the provided token.

        Args:
            token (str): The verification token.
        
        Returns:
            None: The user is verified.

        Raises:
            AuthTokenInvalidError: The token is invalid.
            AuthTokenExpiredError: The token is expired.
            UserNotFoundInDatabaseError: If the user is not found in the database.
            UserStatusInvalidToVerifyEmailError: If the user status is not 
                EMAIL_UNVERIFIED.
        """
        email = self.auth_token_service.decode_token(token)
        
        user = await self.user_repository.get_by_email(email)
        if user is None:
            raise UserNotFoundInDatabaseError(field="email", value=email)
        
        user.verify_email()
        await self.user_repository.update(user)
