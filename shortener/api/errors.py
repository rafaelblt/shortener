import logging
import math

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field, replace
from datetime import timedelta
from http import HTTPStatus
from typing import Any, Final

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from starlette.exceptions import HTTPException

from shortener.api.rate_limit import TooManyRequestsError
from shortener.domain.errors import ShortURLDeactivatedError
from shortener.shared.validation import IssueCode
from shortener.use_cases.errors import (
    InvalidInputError,
    NotAuthenticatedError,
    NothingToUpdateError,
    ShortURLNotFoundError,
)
from shortener.use_cases.shorturl_repository import SlugTakenError
from shortener.use_cases.unavailable_error import UnavailableError


logger = logging.getLogger(__name__)

# The code of the issue of a value a request lacks, besides those of IssueCode.
MISSING: Final = "missing"
_ISSUE_CODES: Final = frozenset(code.value for code in IssueCode)


@dataclass(frozen=True)
class ErrorResponse:
    """How the API answers one kind of error."""

    status_code: HTTPStatus
    code: str
    message: str
    headers: Mapping[str, str] = field(default_factory=dict)


# Every error a use case may return, and how the API answers it. An endpoint
# whose use case returns an error that isn't here fails to be added.
# See docs/api.md#errors
ERRORS: Final[Mapping[type, ErrorResponse]] = {
    NotAuthenticatedError: ErrorResponse(
        HTTPStatus.UNAUTHORIZED,
        "not_authenticated",
        "The request needs a valid access token.",
        headers={"WWW-Authenticate": "Bearer"},
    ),
    InvalidInputError: ErrorResponse(
        HTTPStatus.UNPROCESSABLE_ENTITY,
        "invalid_input",
        "Values of the request break their rules.",
    ),
    NothingToUpdateError: ErrorResponse(
        HTTPStatus.UNPROCESSABLE_ENTITY,
        "nothing_to_update",
        "The request has no value to change.",
    ),
    ShortURLNotFoundError: ErrorResponse(
        HTTPStatus.NOT_FOUND, "shorturl_not_found", "The short URL doesn't exist."
    ),
    ShortURLDeactivatedError: ErrorResponse(
        HTTPStatus.NOT_FOUND, "shorturl_deactivated", "The short URL is deactivated."
    ),
    SlugTakenError: ErrorResponse(
        HTTPStatus.CONFLICT, "slug_taken", "Another short URL has the slug."
    ),
}
MALFORMED_BODY: Final = ErrorResponse(
    HTTPStatus.BAD_REQUEST, "malformed_body", "The body isn't valid JSON."
)
TOO_MANY_REQUESTS: Final = ErrorResponse(
    HTTPStatus.TOO_MANY_REQUESTS,
    "too_many_requests",
    "The client made too many requests. Try again later.",
)
UNAVAILABLE: Final = ErrorResponse(
    HTTPStatus.SERVICE_UNAVAILABLE,
    "unavailable",
    "The service can't answer now. Try again later.",
)
INTERNAL_ERROR: Final = ErrorResponse(
    HTTPStatus.INTERNAL_SERVER_ERROR,
    "internal_error",
    "The service failed to answer the request.",
)


class IssueContent(BaseModel):
    code: str


class FieldContent(BaseModel):
    field: str
    issues: list[IssueContent]


class ErrorContent(BaseModel):
    """The content of every error response."""

    code: str
    message: str
    fields: list[FieldContent] | None = None


def response_of(error_type: type) -> ErrorResponse:
    """
    Raises:
        LookupError: The API doesn't answer errors of the type.
    """
    try:
        return ERRORS[error_type]
    except KeyError:
        raise LookupError(
            f"The API doesn't answer {error_type.__name__}. Add it to ERRORS, "
            "in shortener/api/errors.py"
        ) from None


def error_response(error: object) -> JSONResponse:
    """The response to an error a use case returned."""
    fields = _fields_of(error) if isinstance(error, InvalidInputError) else None
    return _json_response(response_of(type(error)), fields)


def documented_responses(
    error_types: Iterable[type], request_errors: Iterable[ErrorResponse]
) -> dict[int | str, dict[str, Any]]:
    """
    The error responses of an endpoint, for the OpenAPI schema: those of the
    errors of its use case, those of request_errors, TOO_MANY_REQUESTS and
    UNAVAILABLE, grouped by status code.
    """
    errors = [
        *map(response_of, error_types),
        *request_errors,
        TOO_MANY_REQUESTS,
        UNAVAILABLE,
    ]
    by_status: dict[int, dict[str, ErrorResponse]] = {}
    for error in errors:
        by_status.setdefault(error.status_code, {})[error.code] = error
    return {
        status_code: {
            "model": ErrorContent,
            "description": " ".join(
                f"`{error.code}`: {error.message}" for error in by_code.values()
            ),
        }
        for status_code, by_code in by_status.items()
    }


async def request_error_handler(
    request: Request, error: RequestValidationError
) -> JSONResponse:
    details = error.errors()
    if any(detail["type"] == "json_invalid" for detail in details):
        return _json_response(MALFORMED_BODY)
    return _json_response(ERRORS[InvalidInputError], _fields_of_request(details))


async def http_error_handler(request: Request, error: HTTPException) -> JSONResponse:
    """
    The response to the errors Starlette raises on its own, such as for a
    path or a method that no endpoint has. Its code is the name of the
    status, such as not_found.
    """
    status = HTTPStatus(error.status_code)
    response = ErrorResponse(
        status, status.name.lower(), f"{status.phrase}.", headers=error.headers or {}
    )
    return _json_response(response)


async def too_many_requests_handler(
    request: Request, error: TooManyRequestsError
) -> JSONResponse:
    # Retry-After takes whole seconds, so a fraction of a second rounds up.
    seconds = math.ceil(error.retry_after / timedelta(seconds=1))
    return _json_response(
        replace(TOO_MANY_REQUESTS, headers={"Retry-After": str(seconds)})
    )


async def unavailable_handler(
    request: Request, error: UnavailableError
) -> JSONResponse:
    logger.warning(
        "Answered 503 to %s %s", request.method, request.url.path, exc_info=error
    )
    return _json_response(UNAVAILABLE)


async def internal_error_handler(request: Request, error: Exception) -> JSONResponse:
    # The server logs the exception after this response, since Starlette
    # raises it again.
    return _json_response(INTERNAL_ERROR)


def _json_response(
    error: ErrorResponse, fields: list[FieldContent] | None = None
) -> JSONResponse:
    content = ErrorContent(code=error.code, message=error.message, fields=fields)
    return JSONResponse(
        content.model_dump(exclude_none=True),
        status_code=error.status_code,
        headers=dict(error.headers),
    )


def _fields_of(error: InvalidInputError) -> list[FieldContent]:
    return [
        FieldContent(
            field=field_error.field,
            issues=[
                IssueContent(code=issue.code.value)
                for issue in field_error.error.issues
            ],
        )
        for field_error in error.fields
    ]


def _fields_of_request(details: Sequence[Any]) -> list[FieldContent]:
    issues: dict[str, list[IssueContent]] = {}
    for detail in details:
        # The location is the part of the request, then the parameter, such
        # as ("body", "target_url").
        location = detail["loc"]
        field = str(location[1] if len(location) > 1 else location[0])
        issues.setdefault(field, []).append(IssueContent(code=_issue_code(detail)))
    return [FieldContent(field=field, issues=codes) for field, codes in issues.items()]


def _issue_code(detail: Any) -> str:
    # Pydantic names the issues by their type, such as int_parsing. The API
    # keeps the ones that are an IssueCode and MISSING, and answers
    # INVALID_TYPE to the others.
    if detail["type"] == MISSING or detail["type"] in _ISSUE_CODES:
        return detail["type"]
    return IssueCode.INVALID_TYPE.value

