from shortener.domain.user.fields import Email
from shortener.domain.user.exceptions import EmailInvalidError


def validate_email(email: str) -> Email:
    """
    Validate and convert a str to Email object.

    Args:
        email (str): The email string to be validated.

    Returns:
        Email: A valid Email object.

    Raises:
        ValueError: If the email is invalid.
    """
    try:
        return Email(email)
    except EmailInvalidError:
        raise ValueError("The User email is invalid.")
