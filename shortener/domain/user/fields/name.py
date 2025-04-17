import re

from shortener.domain.user.exceptions import (
    UserNameTooLongError, 
    UserNameTooShortError,
    UserNameInvalidPatternError
)


NAME_MAX_LENGTH = 200
NAME_MIN_LENGTH = 2
NAME_REGEX_PATTERN = re.compile(r"^[A-Za-zÀ-ÖØ-öø-ÿ' -]+$")


class Name(str):
    """A custom string class representing a name for User"""

    def __new__(cls, value: str):
        if not isinstance(value, str):
            raise TypeError("Name value arg must be a str.")
        cls.validate_name(value)
        return super().__new__(cls, value)

    def __repr__(self):
        return f"<Name {super().__repr__()}>"

    @staticmethod
    def validate_name(value: str):
        if len(value) > NAME_MAX_LENGTH:
            raise UserNameTooLongError(
                f"Name must be at most {NAME_MAX_LENGTH} characters long."
            )
        
        if len(value) < NAME_MIN_LENGTH:
            raise UserNameTooShortError(
                f"Name must be at least {NAME_MIN_LENGTH} characters long."
            )
        
        if not NAME_REGEX_PATTERN.match(value):
            raise UserNameInvalidPatternError(
                ("Name must contain only letters, spaces, hyphens, "
                 "and apostrophes.")
            )
