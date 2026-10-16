import httpx
import pytest

from http import HTTPStatus

from fastapi import FastAPI
from fastapi.routing import APIRoute

from shortener.api.endpoints import ENDPOINTS
from tests.utils.openapi_helpers import OPENAPI_FILE, openapi_yaml


def test_every_endpoint_is_under_v1(app: FastAPI):
    paths = {route.path for route in app.routes if isinstance(route, APIRoute)}
    assert paths == {f"/v1{endpoint.path}" for endpoint in ENDPOINTS} | {"/v1/health"}


@pytest.mark.parametrize("url", ["/openapi.json", "/docs", "/redoc"])
async def test_does_not_serve_the_documentation(client: httpx.AsyncClient, url: str):
    response = await client.get(url)
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_the_openapi_file_has_the_schema_of_the_app(app: FastAPI):
    assert OPENAPI_FILE.read_text() == openapi_yaml(app), (
        "docs/openapi.yaml is out of date, run `poetry run task openapi`"
    )
