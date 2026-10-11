from collections.abc import Callable, Sequence
from contextlib import AbstractAsyncContextManager
from typing import Final

from fastapi import APIRouter, FastAPI
from fastapi.exceptions import RequestValidationError

from shortener.api.authentication import AccessTokenVerifier
from shortener.api.endpoint import Endpoint, add_route
from shortener.api.endpoints import ENDPOINTS
from shortener.api.errors import (
    internal_error_handler,
    request_error_handler,
    unavailable_handler,
)
from shortener.api.use_case_factory import UseCaseFactory
from shortener.use_cases.unavailable_error import UnavailableError


PREFIX: Final = "/v1"

type Lifespan = Callable[[FastAPI], AbstractAsyncContextManager[None]]


def create_app(
    use_cases: UseCaseFactory,
    access_token_verifier: AccessTokenVerifier,
    endpoints: Sequence[Endpoint] = ENDPOINTS,
    lifespan: Lifespan | None = None,
) -> FastAPI:
    """
    Raises:
        LookupError: The use case of an endpoint may return an error the API
            doesn't answer.
    """
    app = FastAPI(title="Shortener", lifespan=lifespan)
    router = APIRouter(prefix=PREFIX)
    for endpoint in endpoints:
        add_route(router, endpoint, use_cases, access_token_verifier)
    app.include_router(router)
    # The handlers take the class of exception they handle, which FastAPI
    # doesn't type.
    app.add_exception_handler(
        RequestValidationError, request_error_handler  # type: ignore
    )
    app.add_exception_handler(UnavailableError, unavailable_handler)  # type: ignore
    app.add_exception_handler(Exception, internal_error_handler)
    return app
