from shortener.domain.shared.exceptions import ValidationError


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
class ShortURLSuspendedError(ShortURLAvailabilityError): ...
class ShortURLBannedError(ShortURLAvailabilityError): ...


# - VALIDATION EXCEPTIONS
class ShortURLValidationError(ValidationError):
    def __init__(self, value: str | int, field: str, code: str, message: str):
        super().__init__(value, field, code, message)
class ShortURLSlugAlreadyExistsError(ShortURLValidationError):
    code = "SLUG_ALREADY_EXISTS"
    def __init__(self, slug: str):
        self.slug = slug
        msg = f"The provided slug already exists."
        super().__init__(value=slug, field="slug", code=self.code, message=msg)
class ShortURLInvalidSlugError(ShortURLValidationError):
    code = "SLUG_INVALID"
    def __init__(self, slug: str):
        self.slug = slug
        msg = "Slug contains invalid characters. Allowed: a-z, A-Z, 0-9, _, -"
        super().__init__(value=slug, field="slug", code=self.code, message=msg)
class ShortURLForbiddenSlugError(ShortURLValidationError):
    code = "SLUG_FORBIDDEN"
    def __init__(self, slug: str):
        self.slug = slug
        msg = "The provided slug is forbidden."
        super().__init__(value=slug, field="slug", code=self.code, message=msg)
class ShortURLSlugTooLongError(ShortURLValidationError):
    code = "SLUG_TOO_LONG"
    def __init__(self, slug: str, max_length: int):
        self.slug, self.max_length = slug, max_length
        msg = f"Slug must be at least {max_length} characters long."
        super().__init__(value=slug, field="slug", code=self.code, message=msg)
class ShortURLSlugTooShortError(ShortURLValidationError):
    code = "SLUG_TOO_SHORT"
    def __init__(self, slug: str, min_length: int):
        self.slug, self.min_length = slug, min_length
        msg = f"Slug must be at most {min_length} characters long."
        super().__init__(value=slug, field="slug", code=self.code, message=msg)
class ShortURLInvalidURLError(ShortURLValidationError):
    code = "URL_INVALID"
    def __init__(self, url: str):
        self.url = url
        msg = "URL must be a valid https url."
        super().__init__(value=url, field="original_url", code=self.code, message=msg)


# - REPOSITORY EXCEPTIONS
class ShortURLRepositoryError(Exception): ...
class ShortURLInvalidToUpdateError(ShortURLRepositoryError): ...
class ShortURLNotFoundInDatabaseError(ShortURLRepositoryError): ...
class ShortURLNotFoundError(ShortURLRepositoryError):
    def __init__(self, value, field: str):
        self.value = value
        self.field = field
        super().__init__(f"ShortURL with {field}={value} not found.")




class ShortURLDeletionNotFoundError(Exception): ...