class RefreshTokenNotFoundError(Exception):
    def __init__(self, value, field: str):
        self.value = value
        self.field = field
        message = f"RefreshToken with {field}={value} not found."
        super().__init__(message)


class RefreshTokenRevokedError(Exception):
    def __init__(self):
        return super().__init__("The RefreshToken is revoked.")
    

class RefreshTokenExpiredError(Exception):
    def __int__(self):
        return super().__init__("The RefreshToken is expired.")
