from shortener.domain.user import UserRepository
from shortener.domain.user.fields import Email
from shortener.domain.user.exceptions import UserEmailAlreadyExistsError


async def validate_email_exists(email: Email, repository: UserRepository):
    if await repository.exists_by_email(email):
        raise UserEmailAlreadyExistsError(provided_email=email)
