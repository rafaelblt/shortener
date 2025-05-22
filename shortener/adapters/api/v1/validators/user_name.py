from shortener.domain.user.fields import Name
from shortener.domain.user.exceptions import (
    NameTooLongError,
    NameTooShortError,
    NameInvalidPatternError
)

from shortener.adapters.api.v1.exceptions import (
    get_pydantic_name_invalid_pattern_error,
    get_pydantic_name_too_long_error,
    get_pydantic_name_too_short_error
)


def validate_name(name: str) -> Name:
    """
    Validate and convert a str to Name object.

    Args:
        name (str): The name string to be validated.

    Returns:
        Name: A valid Name object.

    Raises:
        ValueError: If the name does not meet the length or pattern constraints.
    """
    try:
        return Name(name)
    except NameTooLongError as e:
        raise get_pydantic_name_too_long_error(input=e.value, max_length=e.max_length)
    except NameTooShortError as e:
        raise get_pydantic_name_too_short_error(input=e.value, min_length=e.min_length)
    except NameInvalidPatternError as e:
        raise get_pydantic_name_invalid_pattern_error(input=e.value)
