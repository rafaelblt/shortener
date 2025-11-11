from typing import Any, Callable
from pydantic import AfterValidator

from shortener.adapters.api.v1.validators.utils import get_pydantic_error_with_validation_error
from shortener.domain.shared.exceptions import ValidationError


class WrapperAfterValidator:

    def __new__(cls, validator_func: Callable[[Any], Any], use_validator_return: bool = False):
        def wrapper(value: Any):
            try:
                retrieved = validator_func(value)
            except ValidationError as e:
                raise get_pydantic_error_with_validation_error(e)
            if use_validator_return:
                return retrieved
            return value
        return AfterValidator(wrapper)
