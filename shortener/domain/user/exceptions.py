class UserAttributeTypeError(TypeError):
    def __init__(self, attr: str, type_expected: str, got):
        super().__init__(
            f"The User {attr} must be an instance of {type_expected}, got "
            f"{type(got).__name__}"
        )


class UserInvalidTimezoneError(ValueError): ...


class UserValidationError(Exception): ...


# Name Validation Exceptions
class NameValidationError(Exception): ...
class NameTooLongError(NameValidationError): 
    def __init__(self, value: str, max_length: int):
        self.value = value
        self.max_length = max_length
        super().__init__(
            f"Name must be at most {max_length} characters long. Got: {value}"
        )
class NameTooShortError(NameValidationError): 
    def __init__(self, value: str, min_length: int):
        self.value = value
        self.min_length = min_length
        super().__init__(
            f"Name must be at least {min_length} characters long. Got: {value}"
        )
class NameInvalidPatternError(NameValidationError): 
    def __init__(self, value: str):
        self.value = value
        super().__init__(
            f"The name '{value}' does not match the required pattern."
        )


# Email Validation Exceptions
class EmailValidationError(Exception): ...
class EmailInvalidError(EmailValidationError): 
    def __init__(self, email: str):
        super().__init__(f"The provided email '{email}' is invalid.")


class UserEmailAlreadyExistsError(UserValidationError): 
    def __init__(self, provided_email: str):
        super().__init__(f"The provided email '{provided_email}' already exists.")
class UserPasswordIncorrectError(UserValidationError):
    def __init__(self):
        super().__init__("The provided password doesn't match.")


class UserRepositoryError(Exception): ...
class UserNotFoundInDatabaseError(UserRepositoryError): ...
