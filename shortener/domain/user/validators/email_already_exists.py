from shortener.domain.shared.validator import Validator
from shortener.domain.shared.email import Email

from shortener.domain.user.repository import UserRepository
from shortener.domain.user.exceptions import EmailAlreadyExistsError


class EmailAlreadyExistsValidator(Validator):
    def __init__(self, repository: UserRepository):
        self.repository = repository

    async def validate(self, value: Email):
        if await self.repository.exists_by_email(value):
            raise EmailAlreadyExistsError(email=value)
