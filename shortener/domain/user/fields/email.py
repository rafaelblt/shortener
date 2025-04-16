import re


EMAIL_REGEX_PATTERN = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")


class Email(str):
    def __new__(cls, value: str):
        value = str(value)
        cls.validate_email(value)
        return super().__new__(cls, value)

    @staticmethod
    def validate_email(value: str):
        if not EMAIL_REGEX_PATTERN.match(value):
            raise TypeError("Email contains invalid characters.")
