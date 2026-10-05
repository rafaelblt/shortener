class DomainError(Exception):
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(f"[{code}]: {message}")


class ValidationError(DomainError):
    def __init__(self, value: str | int, field: str, code: str, message: str):
        self.value = value
        self.field = field
        self.code = code
        self.message = message
        super().__init__(code=code, message=message)


class MultiValidationError(Exception): 
    def __init__(self, errors: list[ValidationError]):
        self.errors = errors
