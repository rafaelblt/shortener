class ValidationError(Exception): ...


# Email Validation Exceptions
class EmailValidationError(ValidationError): ...
class EmailInvalidError(EmailValidationError):
    def __init__(self, email: str):
        super().__init__(f"The provided email '{email}' is invalid.")
