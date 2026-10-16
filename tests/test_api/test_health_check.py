from http import HTTPStatus
from unittest.mock import NonCallableMagicMock

import httpx

from fastapi import FastAPI

from shortener.use_cases.unavailable_error import UnavailableError


async def test_answers_no_content_when_the_health_check_passes(
    client: httpx.AsyncClient, health_check: NonCallableMagicMock
):
    response = await client.get("/v1/health")

    assert response.status_code == HTTPStatus.NO_CONTENT
    assert response.content == b""
    health_check.check.assert_awaited_once_with()


async def test_answers_unavailable_when_the_health_check_raises_unavailable(
    client: httpx.AsyncClient, health_check: NonCallableMagicMock
):
    health_check.check.side_effect = UnavailableError()

    response = await client.get("/v1/health")

    assert response.status_code == HTTPStatus.SERVICE_UNAVAILABLE
    assert response.json()["code"] == "unavailable"


def test_documents_no_content_and_unavailable_without_an_access_token(app: FastAPI):
    operation = app.openapi()["paths"]["/v1/health"]["get"]

    assert set(operation["responses"]) == {
        str(HTTPStatus.NO_CONTENT.value),
        str(HTTPStatus.SERVICE_UNAVAILABLE.value),
    }
    assert "security" not in operation
