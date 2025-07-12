from typing import Callable

from shortener.domain.shared.exceptions import ValidationError

from .utils import get_pydantic_error_with_validation_error


class CustomAfterValidator:

    def __init__(self, validator_func: Callable[[str], None]):
        self.validator = validator_func
    
    def __call__(self, value: str) -> str:
        try:
            self.validator(value)
            return value
        except ValidationError as e:
            raise get_pydantic_error_with_validation_error(e)
