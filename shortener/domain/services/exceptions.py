class AuthTokenError(Exception): ...
class AuthTokenExpiredError(AuthTokenError): 
    def __init__(self, message="Authentication token has expired"):
        super().__init__(message)
class AuthTokenInvalidError(AuthTokenError):
    def __init__(self, message="Authentication token is invalid"):
        super().__init__(message)
