from shortener.domain.user import exceptions


PASSWORD_MIN_LENGTH = 8
PASSWORD_MAX_LENGTH = 128
PASSWORD_SPECIAL_CHARS = "!@#$%^&*()-_=+[]{}|;:'\",.<>/?\\"


class PlainPassword(str):

    def __new__(cls, value: str):
        if not isinstance(value, str):
            raise TypeError("Name value arg must be a str.")
        cls.validate_password(value)
        return super().__new__(cls, value)

    def __str__(self) -> str:
        return super().__str__()

    def __repr__(self):
        return f"<PlainPassword ###>"

    @staticmethod
    def validate_password(value: str):
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
        if len(value) > PASSWORD_MAX_LENGTH:
            raise exceptions.PasswordTooLongError(max_length=PASSWORD_MAX_LENGTH)
        if len(value) < PASSWORD_MIN_LENGTH:
            raise exceptions.PasswordTooShortError(min_length=PASSWORD_MIN_LENGTH)
        if not any(char.isupper() for char in value):
            raise exceptions.PasswordMissingUppercaseError()
        if not any(char.islower() for char in value):
            raise exceptions.PasswordMissingLowercaseError()
        if not any(char.isdigit() for char in value):
            raise exceptions.PasswordMissingDigitError()
        if not any(char in PASSWORD_SPECIAL_CHARS for char in value):
            raise exceptions.PasswordMissingSpecialCharError()
