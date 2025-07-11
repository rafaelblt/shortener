from shortener.domain.shared.exceptions import ValidationError



class AuthTokenError(Exception): ...
class AuthTokenExpiredError(AuthTokenError): 
    def __init__(self, message="Authentication token has expired"):
        super().__init__(message)
class AuthTokenInvalidError(AuthTokenError):
    def __init__(self, message="Authentication token is invalid"):
        super().__init__(message)



class MissingTemplateVariableError(Exception):
    def __init__(self, var_names: list[str]):
        self.var_names = var_names
        super().__init__(f"Missing required template variables: {var_names}")
