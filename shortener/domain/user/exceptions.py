class UserAttributeTypeError(TypeError):
    def __init__(self, attr: str, type_expected: str, got):
        super().__init__(
            f"The User {attr} must be an instance of {type_expected}, not "
            f"{type(got).__name__}"
        )
