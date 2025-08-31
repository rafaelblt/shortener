from shortener.domain.shared.exceptions import ValidationError

from shortener.domain.user.fields.status import UserStatus


class UserAttributeTypeError(TypeError):
    def __init__(self, attr: str, type_expected: str, got):
        super().__init__(
            f"The User {attr} must be an instance of {type_expected}, got "
            f"{type(got).__name__}"
        )
class UserIdIsNotIntError(ValueError):
    def __init__(self, value):
        self.value = value
        super().__init__(
            f"The User id is not an integer. Value: {value} ({value.__class__.__name__})"
        )


class UserStatusInvalidToVerifyEmailError(Exception):
    def __init__(self, status: UserStatus, required_status: UserStatus):
        self.status = status
        self.required_status = required_status
        super().__init__(
            (f"Only users with {required_status} status can be verified. User "
             f"status is {status}")
        )


# User Access Denied Exceptions
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


#
class UserShortURLLimitReachedError(Exception):
    def __init__(self, max_shorturls: int) -> None:
        self.max_shorturls = max_shorturls
        super().__init__(
            f"The maximum number of shorturls ({max_shorturls}) has been reached."
        )


# Name Validation Exceptions
class NameValidationError(ValidationError):
    def __init__(self, value, code, message):
        super().__init__(value=value, field="password", code=code, message=message)

class NameTooLongError(NameValidationError):
    code = "USER_NAME_TOO_LONG"
    def __init__(self, value: str, max_length: int):
        self.value = value
        self.max_length = max_length
        msg = f"Name must be at most {max_length} characters long."
        super().__init__(value=value, code=self.code, message=msg)
    
class NameTooShortError(NameValidationError):
    code = "USER_NAME_TOO_SHORT"
    def __init__(self, value: str, min_length: int):
        self.value = value
        self.min_length = min_length
        msg = f"Name must be at least {min_length} characters long."
        super().__init__(value=value, code=self.code, message=msg)

class NameInvalidPatternError(NameValidationError):
    code = "USER_NAME_INVALID_PATTERN"
    def __init__(self, value: str):
        self.value = value
        msg = "The name does not match the required pattern."
        super().__init__(value=value, code=self.code, message=msg)


class PasswordValidationError(ValidationError):
    def __init__(self, code, message):
        super().__init__(value="***", field="password", code=code, message=message)

class PasswordTooShortError(PasswordValidationError):
    code = "USER_PASSWORD_TOO_SHORT"
    def __init__(self, min_length: int):
        self.min_length = min_length
        msg = f"The password must be at least {self.min_length} characters long."
        super().__init__(code=self.code, message=msg)

class PasswordTooLongError(PasswordValidationError):
    code = "USER_PASSWORD_TOO_LONG"
    def __init__(self, max_length: int):
        self.max_length = max_length
        msg = f"The password must be at most {self.max_length} characters long."
        super().__init__(code=self.code, message=msg)

class PasswordMissingUppercaseError(PasswordValidationError):
    code = "USER_PASSWORD_MISSING_UPPERCASE"
    def __init__(self):
        msg = "The password must contain at least one uppercase character."
        super().__init__(code=self.code, message=msg)

class PasswordMissingLowercaseError(PasswordValidationError):
    code = "USER_PASSWORD_MISSING_LOWERCASE"
    def __init__(self):
        msg = "The password must contain at least one lowercase character."
        super().__init__(code=self.code, message=msg)

class PasswordMissingDigitError(PasswordValidationError):
    code = "USER_PASSWORD_MISSING_DIGIT"
    def __init__(self):
        msg = "The password must contain at least one number."
        super().__init__(code=self.code, message=msg)

class PasswordMissingSpecialCharError(PasswordValidationError):
    code = "USER_PASSWORD_MISSING_SPECIAL_CHAR"
    def __init__(self):
        msg = "The password must contain at least one special character."
        super().__init__(code=self.code, message=msg)


class EmailAlreadyExistsError(ValidationError):
    code = "EMAIL_ALREADY_EXISTS"
    def __init__(self, email: str):
        self.email = email
        msg = f"The provided email already exists."
        super().__init__(value=email, field="email", code=self.code, message=msg)


# User Repository Exceptions
class UserRepositoryError(Exception): ...
class UserNotFoundError(UserRepositoryError): 
    def __init__(self, value, field: str):
        self.value = value
        self.field = field
        super().__init__(f"User with {field}={value} not found.")
