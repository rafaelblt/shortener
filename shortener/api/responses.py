from collections.abc import Callable
from dataclasses import dataclass
from http import HTTPStatus
from typing import Any, ClassVar, Protocol, get_type_hints

from fastapi.responses import JSONResponse, RedirectResponse, Response


class SuccessResponse(Protocol):
    """How an endpoint answers the Ok of its use case. See docs/api.md#responses"""

    status_code: HTTPStatus
    response_class: ClassVar[type[Response]]

    def model(self, ok_type: Any) -> Any:
        """The type of what respond() returns, for FastAPI, or None for none."""
        ...

    def respond(self, value: Any) -> object: ...


@dataclass(frozen=True)
class JSONContent:
    """Answers the value of Ok as JSON, or what encode returns from it."""

    status_code: HTTPStatus = HTTPStatus.OK
    encode: Callable[[Any], object] | None = None
    response_class: ClassVar[type[Response]] = JSONResponse

    def model(self, ok_type: Any) -> Any:
        if self.encode is None:
            return ok_type
        return get_type_hints(self.encode)["return"]

    def respond(self, value: Any) -> object:
        return value if self.encode is None else self.encode(value)


@dataclass(frozen=True)
class NoContent:
    """Answers with no content, whatever the value of Ok."""

    status_code: HTTPStatus = HTTPStatus.NO_CONTENT
    response_class: ClassVar[type[Response]] = Response

    def model(self, ok_type: Any) -> None:
        return None

    def respond(self, value: Any) -> Response:
        return Response(status_code=self.status_code)


@dataclass(frozen=True)
class Redirect:
    """Redirects to the URL that location returns from the value of Ok."""

    location: Callable[[Any], str]
    status_code: HTTPStatus = HTTPStatus.TEMPORARY_REDIRECT
    response_class: ClassVar[type[Response]] = RedirectResponse

    def model(self, ok_type: Any) -> None:
        return None

    def respond(self, value: Any) -> Response:
        return RedirectResponse(self.location(value), status_code=self.status_code)
