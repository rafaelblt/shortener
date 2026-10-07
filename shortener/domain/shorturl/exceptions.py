class ShortURLAttributeTypeError(TypeError):
    def __init__(self, attr: str, type_expected: str, got):
        super().__init__(
            f"The ShortURL {attr} must be an instance of {type_expected}, got "
            f"{type(got).__name__}"
        )


# AVAILABILITY EXCEPTIONS
class ShortURLAvailabilityError(Exception): ...
class ShortURLDeactivatedError(ShortURLAvailabilityError): ...
class ShortURLExpiredError(ShortURLAvailabilityError): ...
