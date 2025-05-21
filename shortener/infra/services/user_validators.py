from shortener.domain.user import UserRepository
from shortener.domain.user.fields import Email
from shortener.domain.user.exceptions import EmailAlreadyExistsError

from shortener.domain.shared.validator import Validator


class EmailExistsValidator(Validator):
    def __init__(self, repository: UserRepository):
        self.repository = repository

    async def validate(self, value: Email):
        if await self.repository.exists_by_email(value):
            raise EmailAlreadyExistsError(email=value)
