from typing import Protocol

from fastapi import APIRouter

from shortener.api.errors import documented_responses
from shortener.api.responses import NoContent


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
    Adds GET /health, which answers 204 when health_check passes.
    See docs/api.md#health-check
    """
    response = NoContent()

    async def check_health() -> object:
        await health_check.check()
        return response.respond(None)

    router.add_api_route(
        "/health",
        check_health,
        methods=["GET"],
        status_code=response.status_code,
        response_model=None,
        response_class=response.response_class,
        responses=documented_responses([]),
        name="CheckHealth",
        operation_id="CheckHealth",
    )
