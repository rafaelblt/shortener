from shortener.domain.user.exceptions import UserNotFoundError

from shortener.domain.services.token import TokenService, TokenInvalidError

from shortener.domain.user import UserRepository


class VerifyEmailUseCase:
    """Use Case to verify a user's email address."""

    def __init__(
        self,
        user_repository: UserRepository,
        token_service: TokenService
    ):
        """
        Args:
            user_repository: Repository to find and update the user.
            token_service: Service to decode the verify token.
        """
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
        payload = self.token_service.decode_token(token)

        if not payload["purpose"] == self.token_service.Purpose.EMAIL_VERIFICATION:
            raise TokenInvalidError()
        
        email = payload["subject"]
        user = await self.user_repository.get_by_email(email)
        if user is None:
            raise UserNotFoundError(field="email", value=email)
        
        user.verify_email()
        await self.user_repository.update(user)
