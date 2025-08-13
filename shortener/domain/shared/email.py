import re

from .exceptions import EmailInvalidError


EMAIl_REGEX = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"


class Email(str):
    def __new__(cls, value: str):
        if not isinstance(value, str):
            raise TypeError("Email value arg must be a str.")
        cls.validate_email(value)
        return super().__new__(cls, value)

    def __repr__(self):
        return f"<Email {super().__repr__()}>"

    @staticmethod
    def validate_email(value: str):
        if not re.match(EMAIl_REGEX, value):
            raise EmailInvalidError(email=value)            
