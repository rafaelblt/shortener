from typing import Any, Callable
from datetime import timedelta

from shortener.domain.shared.email import Email
from shortener.domain.shared.exceptions import EmailInvalidError


ConverterFunc = Callable[[str], Any]


class ConversionError(Exception): ...


def convert_str_minutes_to_timedelta(input: str):
    try:
        minutes = int(input)
    except (ValueError, TypeError):
        raise ConversionError(
            f"The value '{input}' could not be converted to an integer."
        )
    return timedelta(minutes=minutes)


def convert_str_to_email(input: str):
    try:
        email = Email(input)
    except EmailInvalidError:
        raise ConversionError(
            f"The value '{input}' is not a valid email address."
        )
    return email
