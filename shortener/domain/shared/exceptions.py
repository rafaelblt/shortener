class DomainError(Exception):
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(f"[{code}]: {message}")


class ValidationError(DomainError):
    def __init__(self, value: str | int, field: str, code: str, message: str):
        self.value = value
        self.field = field
        self.code = code
        self.message = message
        super().__init__(code=code, message=message)


class MultiValidationError(Exception): 
    def __init__(self, errors: list[ValidationError]):
        self.errors = errors


class EmailValidationError(ValidationError):
    def __init__(self, value: str, code: str, message: str):
        super().__init__(value=value, field="email", code=code, message=message)

class EmailInvalidError(EmailValidationError):
    code = "EMAIL_INVALID"

    def __init__(self, email: str):
        msg = "The provided email is invalid."
        super().__init__(value=email, code=self.code, message=msg)
