from shortener.domain.user.fields import Name
from shortener.domain.user.exceptions import (
    NameTooLongError,
    NameTooShortError,
    NameInvalidPatternError
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
        raise ValueError(
            f"The User name must be at most {e.max_length} characters long."
        )
    except NameTooShortError as e:
        raise ValueError(
            f"The User name must be at least {e.min_length} characters long."
        )
    except NameInvalidPatternError as e:
        raise ValueError("The User name does not match the required pattern.")
