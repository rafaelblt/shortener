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


class PasswordValidatorService:
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

    def validate(self, password: str):
        """
        Validate whether a provided password is valid.

        Args:
            password (str): The plain password to be validated.

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
        if len(password) > self.max_length:
            raise PasswordTooLongError(value=password, max_length=self.max_length)
        if len(password) < self.min_length:
            raise PasswordTooShortError(value=password, min_length=self.min_length)
        if not any(char.isupper() for char in password):
            raise PasswordMissingUppercaseError(value=password)
        if not any(char.islower() for char in password):
            raise PasswordMissingLowercaseError(value=password)
        if not any(char.isdigit() for char in password):
            raise PasswordMissingDigitError(value=password)
        if not any(char in self.special_chars for char in password):
            raise PasswordMissingSpecialCharError(value=password)
