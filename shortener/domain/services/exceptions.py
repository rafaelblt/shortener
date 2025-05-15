class AuthTokenError(Exception): ...
class AuthTokenExpiredError(AuthTokenError): 
    def __init__(self, message="Authentication token has expired"):
        super().__init__(message)
class AuthTokenInvalidError(AuthTokenError):
    def __init__(self, message="Authentication token is invalid"):
        super().__init__(message)



class PasswordValidationError(Exception): ...
class PasswordTooShortError(PasswordValidationError):
    def __init__(self, value: str, min_length: int):
        self.value = value
        self.min_length = min_length
        super().__init__(
            (f"The password must be at least {self.min_length} characters long."
             f"Got (len={len(self.value)}): {self.value}")
        )
class PasswordTooLongError(PasswordValidationError):
    def __init__(self, value: str, max_length: int):
        self.value = value
        self.max_length = max_length
        super().__init__(
            (f"The password must be at most {self.max_length} characters long. "
             f"Got (len={len(self.value)}): {self.value}")
        )
class PasswordMissingUppercaseError(PasswordValidationError):
    def __init__(self, value: str):
        self.value = value
        super().__init__(
            (f"The password must contain at least one uppercase character. "
             f"Got: {self.value}")
        )
class PasswordMissingLowercaseError(PasswordValidationError):
    def __init__(self, value: str):
        self.value = value
        super().__init__(
            (f"The password must contain at least one lowercase character. "
             f"Got: {self.value}")
        )
class PasswordMissingDigitError(PasswordValidationError):
    def __init__(self, value: str):
        self.value = value
        super().__init__(
            f"The password must contain at least one number. Got: {self.value}"
        )
class PasswordMissingSpecialCharError(PasswordValidationError):
    def __init__(self, value: str):
        self.value = value
        super().__init__(
            (f"The password must contain at least one special character. "
             f"Got: {self.value}")
        )
