from dataclasses import dataclass

from shortener.shared.result import Err, Result
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


def collect_field_errors(
    **results: Result[object, ValidationError],
) -> tuple[FieldError, ...]:
    """
    Returns a FieldError for each result that is an Err, with the keyword
    of the result as the field, in the order of the keywords.
    """
    return tuple(
        FieldError(field, result.error)
        for field, result in results.items()
        if isinstance(result, Err)
    )
