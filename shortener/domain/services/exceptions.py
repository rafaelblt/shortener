class AuthTokenError(Exception): ...
class AuthTokenExpiredError(AuthTokenError): 
    def __init__(self, message="Authentication token has expired"):
        super().__init__(message)
class AuthTokenInvalidError(AuthTokenError):
    def __init__(self, message="Authentication token is invalid"):
        super().__init__(message)


class TokenError(Exception): ...
class TokenExpiredError(TokenError): 
    def __init__(self, message="Token has expired"):
        super().__init__(message)
class TokenInvalidError(TokenError):
    def __init__(self, message="Token is invalid"):
        super().__init__(message)


class MissingTemplateVariableError(Exception):
    def __init__(self, var_names: list[str]):
        self.var_names = var_names
        super().__init__(f"Missing required template variables: {var_names}")
