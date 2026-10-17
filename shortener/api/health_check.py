import logging

from http import HTTPStatus
from typing import Protocol

from fastapi import APIRouter, Request, Response

from shortener.api.errors import log_unavailable
from shortener.api.responses import NoContent
from shortener.use_cases.unavailable_error import UnavailableError


logger = logging.getLogger(__name__)


class HealthCheck(Protocol):
    async def check(self) -> None:
        """
        Returns when the service is able to answer.

        Raises:
            UnavailableError: Something the service needs to answer, such as
                the database, is unavailable.
        """
        ...


def add_health_check_route(router: APIRouter, health_check: HealthCheck) -> None:
    """
    Adds GET /health, which answers only a status code, by what health_check
    does. See docs/architecture/api.md#health-check
    """
    response = NoContent()

    async def check_health(request: Request) -> Response:
        try:
            await health_check.check()
        except UnavailableError as error:
            log_unavailable(request, error)
            return Response(status_code=HTTPStatus.SERVICE_UNAVAILABLE)
        except Exception:
            # Answered here, the exception doesn't reach the server, which
            # logs those of the other routes.
            logger.exception("Answered 500 to %s %s", request.method, request.url.path)
            return Response(status_code=HTTPStatus.INTERNAL_SERVER_ERROR)
        return response.respond(None)

    router.add_api_route(
        "/health",
        check_health,
        methods=["GET"],
        status_code=response.status_code,
        response_model=None,
        response_class=response.response_class,
        response_description=response.status_code.phrase,
        responses={
            HTTPStatus.SERVICE_UNAVAILABLE: {
                "description": HTTPStatus.SERVICE_UNAVAILABLE.phrase
            }
        },
        summary="Check the health of the service",
        tags=["Health"],
        name="CheckHealth",
        operation_id="CheckHealth",
    )
