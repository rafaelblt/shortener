from email_validator import validate_email as lib_validate_email

from shortener.domain.user.exceptions import EmailInvalidError


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
        try:
            lib_validate_email(value)
        except Exception:
            raise EmailInvalidError(email=value)
