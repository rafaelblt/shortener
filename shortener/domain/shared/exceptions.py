from typing import TypedDict


class ValidationError(Exception): 
    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message
        super().__init__(f"[{code}]: {message}")


class FieldValidationError(Exception):
    def __init__(self, field_name: str, input: str, validation_errors: list[ValidationError]):
        self.input = input
        self.field = field_name
        self.validation_errors = validation_errors
        validation_errors_codes = [error.code for error in validation_errors]
        super().__init__(
            f"The field {field_name} (input: {input}) has validation errors: {validation_errors_codes}"
        )


class MultiFieldValidationError(Exception): 
    def __init__(self, field_validation_errors: list[FieldValidationError]):
        pass

# Email Validation Exceptions
class EmailValidationError(FieldValidationError):
    def __init__(self, input: str, validation_errors: list[ValidationError]):
        super().__init__(field_name="email", input=input, validation_errors=validation_errors)

class EmailInvalidError(EmailValidationError):
    def __init__(self, email: str):
        validation_error = ValidationError(
            code="EMAIL_INVALID", message="The provided email is invalid."
        )
        super().__init__(input=email, validation_errors=[validation_error])
