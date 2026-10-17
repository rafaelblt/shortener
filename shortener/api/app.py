from collections.abc import Callable, Sequence
from contextlib import AbstractAsyncContextManager

from fastapi import APIRouter, Depends, FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException

from shortener.api.authentication import AccessTokenVerifier
from shortener.api.endpoint import Endpoint, add_route
from shortener.api.endpoints import ENDPOINTS
from shortener.api.errors import (
    http_error_handler,
    internal_error_handler,
    request_error_handler,
    too_many_requests_handler,
    unavailable_handler,
)
from shortener.api.health_check import HealthCheck, add_health_check_route
from shortener.api.prefix import PREFIX
from shortener.api.rate_limit import RateLimiter, TooManyRequestsError, limit_by_ip
from shortener.api.use_case_factory import UseCaseFactory
from shortener.use_cases.unavailable_error import UnavailableError


type Lifespan = Callable[[FastAPI], AbstractAsyncContextManager[None]]


def create_app(
    use_cases: UseCaseFactory,
    access_token_verifier: AccessTokenVerifier,
    rate_limiter: RateLimiter,
    health_check: HealthCheck,
    endpoints: Sequence[Endpoint] = ENDPOINTS,
    lifespan: Lifespan | None = None,
) -> FastAPI:
    """
    Raises:
        LookupError: The use case of an endpoint may return an error the API
            doesn't answer.
    """
    # The OpenAPI schema is in docs/service/openapi.yaml instead of being served.
    # See docs/architecture/api.md#openapi
    app = FastAPI(
        title="Shortener",
        lifespan=lifespan,
        openapi_url=None,
        docs_url=None,
        redoc_url=None,
    )
    router = APIRouter(prefix=PREFIX, dependencies=[Depends(limit_by_ip(rate_limiter))])
    for endpoint in endpoints:
        add_route(router, endpoint, use_cases, access_token_verifier)
    app.include_router(router)
    # Out of PREFIX, since it isn't part of the versioned API, and out of the
    # rate limit, so an orchestrator or a load balancer that checks the health
    # often doesn't get too_many_requests.
    add_health_check_route(app.router, health_check)
    # The handlers take the class of exception they handle, which FastAPI
    # doesn't type.
    app.add_exception_handler(
        RequestValidationError,
        request_error_handler,  # type: ignore[arg-type]
    )
    app.add_exception_handler(HTTPException, http_error_handler)  # type: ignore[arg-type]
    app.add_exception_handler(
        TooManyRequestsError,
        too_many_requests_handler,  # type: ignore[arg-type]
    )
    app.add_exception_handler(UnavailableError, unavailable_handler)  # type: ignore[arg-type]
    app.add_exception_handler(Exception, internal_error_handler)
    return app
