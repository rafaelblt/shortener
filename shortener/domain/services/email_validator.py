from abc import ABC, abstractmethod
from shortener.domain.user.fields import Email


class EmailValidatorService(ABC):

    @abstractmethod
    async def validate(self, email: Email) -> None:
        pass
