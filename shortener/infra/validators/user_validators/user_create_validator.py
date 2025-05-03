from shortener.domain.user import User, UserValidator, UserRepository

from .email_exists_validator import validate_email_exists


class UserCreateValidator(UserValidator):
    """User Validator class to validate a User to be created"""

    def __init__(self, repository: UserRepository):
        self.repository = repository

    async def validate(self, user: User):
        await validate_email_exists(slug=user.slug, repository=self.repository)
