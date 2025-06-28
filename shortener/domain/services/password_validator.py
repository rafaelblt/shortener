from shortener.domain.shared.validator import Validator

from .exceptions import (
    PasswordTooShortError,
    PasswordTooLongError,
    PasswordMissingUppercaseError,
    PasswordMissingLowercaseError,
    PasswordMissingDigitError,
    PasswordMissingSpecialCharError
)


PASSWORD_MIN_LENGTH = 8
PASSWORD_MAX_LENGTH = 128
PASSWORD_SPECIAL_CHARS = "!@#$%^&*()-_=+[]{}|;:'\",.<>/?\\"


class PasswordStrengthValidator(Validator):
    """Service to validate password security and strength."""

    def __init__(
        self,
        min_length: int = PASSWORD_MIN_LENGTH,
        max_length: int = PASSWORD_MAX_LENGTH,
        special_chars: str = PASSWORD_SPECIAL_CHARS
    ):
        self.min_length = min_length
        self.max_length = max_length
        self.special_chars = special_chars

    async def validate(self, value: str):
        """
        Validate whether a provided password is valid.

        Args:
            value (str): The plain password to be validated.

        Returns:
            None: The password is valid.

        Raises:
            PasswordTooShortError: The password is less than min length.
            PasswordTooLongError: The password is longer than max length.
            PasswordMissingUppercaseError: The password doesnt contain uppercase chars.
            PasswordMissingLowercaseError: The password doesnt contain lowercase chars.
            PasswordMissingDigitError: The password doesnt contain numbers.
            PasswordMissingSpecialCharError: The password doesnt contain special chars.
        """
        if len(value) > self.max_length:
            raise PasswordTooLongError(value=value, max_length=self.max_length)
        if len(value) < self.min_length:
            raise PasswordTooShortError(value=value, min_length=self.min_length)
        if not any(char.isupper() for char in value):
            raise PasswordMissingUppercaseError(value=value)
        if not any(char.islower() for char in value):
            raise PasswordMissingLowercaseError(value=value)
        if not any(char.isdigit() for char in value):
            raise PasswordMissingDigitError(value=value)
        if not any(char in self.special_chars for char in value):
            raise PasswordMissingSpecialCharError(value=value)
