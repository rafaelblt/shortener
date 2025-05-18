from abc import ABC, abstractmethod


class NameValidatorService(ABC):

    @abstractmethod
    async def validate(self, name: str) -> None:
        pass
