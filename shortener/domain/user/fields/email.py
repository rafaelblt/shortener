import re

from shortener.domain.user.exceptions import UserEmailInvalidPatternError


EMAIL_REGEX_PATTERN = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")


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
        if not EMAIL_REGEX_PATTERN.match(value):
            raise UserEmailInvalidPatternError("Email contains invalid characters.")
