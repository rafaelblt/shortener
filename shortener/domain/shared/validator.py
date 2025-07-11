import asyncio

from types import CoroutineType
from abc import ABC, abstractmethod

from shortener.domain.shared.exceptions import ValidationError, MultiValidationError


class Validator(ABC):

    @abstractmethod
    async def validate(self, value) -> None:
        pass


class MultiFieldValidator:

    def __init__(self, validators_map: dict[str, list[Validator]]):
        self.validators_map = validators_map

    async def validate(self, **kwargs):
        coros = self._get_validation_coros(**kwargs)
        results = await asyncio.gather(*coros, return_exceptions=True)
        errors = self._search_errors(results)
        if errors:
            raise MultiValidationError(errors)
        return None
    
    def _get_validation_coros(self, **kwargs) -> list[CoroutineType]:
        coros: list[CoroutineType] = []
        for key, value in kwargs.items():
            validators = self.validators_map.get(key, [])
            for validator in validators:
                coro = validator.validate(value)
                coros.append(coro)
        return coros

    def _search_errors(self, results: list) -> list[ValidationError]:
        errors: list[ValidationError] = []
        for result in results:
            if isinstance(result, ValidationError):
                errors.append(result)
        return errors
