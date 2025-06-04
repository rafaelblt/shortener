from shortener.domain.user.fields import Email
from shortener.domain.shared.exceptions import EmailInvalidError

from shortener.adapters.api.v1.exceptions import get_pydantic_email_invalid_error


def validate_email(email: str) -> Email:
    """
    Validate and convert a str to Email object.

    Args:
        email (str): The email string to be validated.

    Returns:
        Email: A valid Email object.

    Raises:
        PydanticCustomError: If the email is invalid.
    """
    try:
        return Email(email)
    except EmailInvalidError:
        raise get_pydantic_email_invalid_error(input=email)
