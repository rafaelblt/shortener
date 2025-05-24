from shortener.domain.shared.exceptions import ValidationError


class UserAttributeTypeError(TypeError):
    def __init__(self, attr: str, type_expected: str, got):
        super().__init__(
            f"The User {attr} must be an instance of {type_expected}, got "
            f"{type(got).__name__}"
        )


class UserAccessDeniedError(Exception): ...
class UserEmailNotVerifiedError(UserAccessDeniedError):
    def __init__(self):
        super().__init__("The User email has not been verified.")
class UserLockedError(UserAccessDeniedError):
    def __init__(self):
        super().__init__("The User has been locked.")
class UserSuspendedError(UserAccessDeniedError):
    def __init__(self):
        super().__init__("The User has been suspended.")
class UserBannedError(UserAccessDeniedError):
    def __init__(self):
        super().__init__("The User has been banned.")
class UserPasswordIncorrectError(UserAccessDeniedError):
    def __init__(self):
        super().__init__("The provided password doesn't match.")


# Name Validation Exceptions
class NameValidationError(ValidationError): ...
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
class EmailValidationError(ValidationError): ...
class EmailInvalidError(EmailValidationError):
    def __init__(self, email: str):
        super().__init__(f"The provided email '{email}' is invalid.")
class EmailAlreadyExistsError(EmailValidationError):
    def __init__(self, email: str):
        self.email = email
        super().__init__(f"The provided email '{email}' already exists.")


# User Repository Exceptions
class UserRepositoryError(Exception): ...
class UserNotFoundInDatabaseError(UserRepositoryError): 
    def __init__(self, value, field: str):
        self.value = value
        self.field = field
        super().__init__(f"User with {field}={value} not found in the database.")
