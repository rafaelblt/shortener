from shortener.domain.shared.exceptions import ValidationError
from pydantic_core import PydanticCustomError

def get_pydantic_error_with_validation_error(error: ValidationError):
    return PydanticCustomError(error.code, error.message) # type: ignore
