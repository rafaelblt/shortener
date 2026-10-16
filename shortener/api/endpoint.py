import inspect
import re

from dataclasses import KW_ONLY, dataclass
from types import UnionType
from typing import Annotated, Any, Final, Union, get_args, get_origin, get_type_hints

from fastapi import APIRouter, Body, Depends, Path, Query, params
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from shortener.api.authentication import AccessTokenCurrentUser, AccessTokenVerifier
from shortener.api.cursors import CursorParameter
from shortener.api.errors import (
    ERRORS,
    MALFORMED_BODY,
    TOO_MANY_REQUESTS,
    ErrorResponse,
    documented_responses,
    error_response,
    response_of,
)
from shortener.api.responses import JSONContent, SuccessResponse
from shortener.api.use_case_factory import UseCaseFactory
from shortener.shared.result import Err, Ok
from shortener.use_cases.current_user import CurrentUser
from shortener.use_cases.errors import InvalidInputError
from shortener.use_cases.shorturl_cursor import ShortURLCursor


# How a request carries the parameters of execute() whose type FastAPI
# doesn't read on its own. See docs/api.md#how-an-endpoint-works
PARAMETER_TYPES: Final[dict[Any, Any]] = {ShortURLCursor: CursorParameter}

METHODS_WITHOUT_BODY: Final = frozenset({"GET", "DELETE"})

_bearer = HTTPBearer(auto_error=False)
_CREDENTIALS: Final = inspect.Parameter(
    "_credentials",
    inspect.Parameter.KEYWORD_ONLY,
    annotation=Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
)


@dataclass(frozen=True)
class Endpoint:
    """
    An endpoint that runs a use case. What it receives and what it answers
    come from the use case. Its name is the one of the use case when name is
    None. See docs/api.md#endpoints
    """

    method: str
    path: str
    use_case: type
    response: SuccessResponse = JSONContent()
    _: KW_ONLY
    summary: str
    name: str | None = None


def add_route(
    router: APIRouter,
    endpoint: Endpoint,
    use_cases: UseCaseFactory,
    access_token_verifier: AccessTokenVerifier,
) -> None:
    """
    Raises:
        LookupError: The use case may return an error the API doesn't answer.
    """
    name = endpoint.name or endpoint.use_case.__name__
    parameters = _parameters_of(endpoint)
    ok_type, error_types = _result_types_of(endpoint.use_case)
    takes_a_user = CurrentUser in get_type_hints(endpoint.use_case.__init__).values()

    async def run(**arguments: Any) -> object:
        credentials = arguments.pop(_CREDENTIALS.name, None)
        current_user = AccessTokenCurrentUser(
            credentials.credentials if credentials is not None else None,
            access_token_verifier,
        )
        use_case: Any = use_cases.build(endpoint.use_case, current_user)
        match await use_case.execute(**arguments):
            case Ok(value):
                return endpoint.response.respond(value)
            case Err(error):
                return error_response(error)

    # FastAPI reads what to receive from the signature of the function.
    run.__signature__ = inspect.Signature(  # type: ignore
        [*parameters, _CREDENTIALS] if takes_a_user else parameters
    )
    router.add_api_route(
        endpoint.path,
        run,
        methods=[endpoint.method],
        status_code=endpoint.response.status_code,
        response_model=endpoint.response.model(ok_type),
        response_class=endpoint.response.response_class,
        responses=documented_responses(
            [
                *map(response_of, error_types),
                *_request_errors_of(parameters),
                TOO_MANY_REQUESTS,
            ]
        ),
        summary=endpoint.summary,
        name=name,
        operation_id=name,
    )


def _parameters_of(endpoint: Endpoint) -> list[inspect.Parameter]:
    execute = endpoint.use_case.execute
    types = get_type_hints(execute)
    in_path = set(re.findall(r"{(\w+)}", endpoint.path))
    return [
        inspect.Parameter(
            name,
            inspect.Parameter.KEYWORD_ONLY,
            default=parameter.default,
            annotation=Annotated[
                _received_type(types[name]), _source(endpoint.method, name in in_path)
            ],
        )
        for name, parameter in inspect.signature(execute).parameters.items()
        if name != "self"
    ]


def _source(method: str, is_in_path: bool) -> params.Param | params.Body:
    if is_in_path:
        return Path()
    if method in METHODS_WITHOUT_BODY:
        return Query()
    return Body(embed=True)


def _received_type(type_: Any) -> Any:
    if get_origin(type_) in (Union, UnionType):
        return Union[tuple(_received_type(member) for member in get_args(type_))]
    return PARAMETER_TYPES.get(type_, type_)


def _result_types_of(use_case: type) -> tuple[Any, tuple[type, ...]]:
    # execute() returns Result[Ok, Error], whose Error is a type alias of a
    # union, such as CreateShortURLError, or a single class.
    ok_type, error = get_args(get_type_hints(use_case.execute)["return"])
    errors = getattr(error, "__value__", error)
    return ok_type, get_args(errors) or (errors,)


def _request_errors_of(parameters: list[inspect.Parameter]) -> list[ErrorResponse]:
    """The errors FastAPI may raise when it reads the parameters."""
    if not parameters:
        return []
    sources = [get_args(parameter.annotation)[1] for parameter in parameters]
    if any(isinstance(source, params.Body) for source in sources):
        return [ERRORS[InvalidInputError], MALFORMED_BODY]
    return [ERRORS[InvalidInputError]]
