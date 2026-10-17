import logging

from http import HTTPStatus
from unittest.mock import NonCallableMagicMock

import httpx
import pytest

from fastapi import FastAPI

from shortener.use_cases.unavailable_error import UnavailableError


async def test_answers_no_content_when_the_health_check_passes(
    client: httpx.AsyncClient, health_check: NonCallableMagicMock
):
    response = await client.get("/health")

    assert response.status_code == HTTPStatus.NO_CONTENT
    assert response.content == b""
    health_check.check.assert_awaited_once_with()


@pytest.mark.parametrize(
    "error, status",
    [
        pytest.param(
            UnavailableError(), HTTPStatus.SERVICE_UNAVAILABLE, id="unavailable"
        ),
        pytest.param(
            RuntimeError(), HTTPStatus.INTERNAL_SERVER_ERROR, id="any other exception"
        ),
    ],
)
async def test_answers_only_the_status_of_what_the_health_check_raises(
    client: httpx.AsyncClient,
    health_check: NonCallableMagicMock,
    error: Exception,
    status: HTTPStatus,
):
    health_check.check.side_effect = error

    response = await client.get("/health")

    assert response.status_code == status
    assert response.content == b""


@pytest.mark.parametrize(
    "error, level",
    [
        pytest.param(UnavailableError(), logging.WARNING, id="unavailable"),
        pytest.param(RuntimeError(), logging.ERROR, id="any other exception"),
    ],
)
async def test_logs_what_the_health_check_raises(
    client: httpx.AsyncClient,
    health_check: NonCallableMagicMock,
    caplog: pytest.LogCaptureFixture,
    error: Exception,
    level: int,
):
    health_check.check.side_effect = error

    with caplog.at_level(logging.WARNING):
        await client.get("/health")

    [record] = caplog.records
    assert record.levelno == level
    assert record.exc_info is not None
    assert record.exc_info[1] is error


def test_documents_no_content_and_unavailable_without_content_nor_access_token(
    app: FastAPI,
):
    operation = app.openapi()["paths"]["/health"]["get"]

    assert set(operation["responses"]) == {
        str(HTTPStatus.NO_CONTENT.value),
        str(HTTPStatus.SERVICE_UNAVAILABLE.value),
    }
    assert all(
        "content" not in response for response in operation["responses"].values()
    )
    assert "security" not in operation
