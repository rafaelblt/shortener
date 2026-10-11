from dataclasses import dataclass

from shortener.shared.validation import ValidationError


@dataclass(frozen=True)
class NotAuthenticatedError: ...


@dataclass(frozen=True)
class ShortURLNotFoundError: ...


@dataclass(frozen=True)
class FieldError:
    field: str
    error: ValidationError


@dataclass(frozen=True)
class InvalidInputError:
    fields: tuple[FieldError, ...]


@dataclass(frozen=True)
class NothingToUpdateError: ...
