import asyncio

from types import CoroutineType
from abc import ABC, abstractmethod

from shortener.domain.shared.exceptions import ValidationError, FieldValidationError


class Validator(ABC):

    @abstractmethod
    async def validate(self, value):
        pass


class MultiFieldValidator:

    def __init__(self, validators_map: dict[str, list[Validator]]):
        self.validators_map = validators_map

    async def validate(self, **kwargs):
        validations: list[tuple[str, CoroutineType]] = []

        for key, value in kwargs.items():
            validators = self.validators_map.get(key, [])
            for validator in validators:
                coro = validator.validate(value)
                validation = (key, coro)
                validations.append(validation)

        coros = [coro for _, coro in validations]

        results = await asyncio.gather(*coros, return_exceptions=True)
        
        errors: dict[str, list[ValidationError]] = {}
        for field in kwargs:
            errors[field] = []

        for i, result in enumerate(results):
            if isinstance(result, ValidationError):
                field = validations[i][0]
                errors[field].append(result)
        
        if errors:
            return errors
