import httpx
import pytest

from datetime import timedelta
from http import HTTPStatus
from unittest.mock import NonCallableMagicMock

from fastapi import FastAPI

from shortener.api.endpoint import Endpoint
from shortener.api.endpoints import ENDPOINTS
from shortener.shared.result import Ok
from shortener.use_cases.resolve_slug import ResolveSlug
from shortener.use_cases.resolved_slug import ResolvedSlug
from tests.fixtures.api.doubles import UseCaseDoubles


ADDRESS = ("203.0.113.7", 50000)
ID = "0199b2c4-7a3e-7c1a-9b5e-3f2d4c6b8a20"
RESOLVE_URL = "/v1/slugs/my-slug"


def client_from(app: FastAPI, address: tuple[str, int] | None) -> httpx.AsyncClient:
    """A client of the app whose requests come from the address."""
    transport = httpx.ASGITransport(app=app, client=address)  # type: ignore[arg-type]
    return httpx.AsyncClient(transport=transport, base_url="http://test")


@pytest.fixture
def resolve_slug(use_cases: UseCaseDoubles) -> NonCallableMagicMock:
    resolve_slug = use_cases.double(ResolveSlug)
    resolve_slug.execute.return_value = Ok(ResolvedSlug("https://example.com"))
    return resolve_slug


@pytest.fixture
def over_the_limit(rate_limiter: NonCallableMagicMock) -> NonCallableMagicMock:
    rate_limiter.hit.return_value = timedelta(seconds=30)
    return rate_limiter


async def test_counts_each_request_under_the_ip_address_of_its_client(
    app: FastAPI, rate_limiter: NonCallableMagicMock, resolve_slug: NonCallableMagicMock
):
    async with client_from(app, ADDRESS) as client:
        await client.get(RESOLVE_URL)

    rate_limiter.hit.assert_called_once_with(ADDRESS[0])


async def test_runs_the_use_case_when_the_ip_address_is_within_its_limit(
    client: httpx.AsyncClient, resolve_slug: NonCallableMagicMock
):
    response = await client.get(RESOLVE_URL)

    assert response.status_code == HTTPStatus.OK
    resolve_slug.execute.assert_awaited_once()


async def test_answers_too_many_requests_without_building_the_use_case_over_the_limit(
    client: httpx.AsyncClient,
    use_cases: UseCaseDoubles,
    over_the_limit: NonCallableMagicMock,
):
    response = await client.get(RESOLVE_URL)

    assert response.status_code == HTTPStatus.TOO_MANY_REQUESTS
    assert response.json()["code"] == "too_many_requests"
    assert use_cases.current_users == []


@pytest.mark.parametrize(
    "retry_after, header",
    [
        pytest.param(timedelta(seconds=30), "30", id="whole seconds"),
        pytest.param(timedelta(seconds=29, microseconds=1), "30", id="fraction"),
        pytest.param(timedelta(microseconds=1), "1", id="less than a second"),
    ],
)
async def test_answers_when_to_retry_in_whole_seconds_rounded_up(
    client: httpx.AsyncClient,
    rate_limiter: NonCallableMagicMock,
    retry_after: timedelta,
    header: str,
):
    rate_limiter.hit.return_value = retry_after

    response = await client.get(RESOLVE_URL)

    assert response.headers["Retry-After"] == header


@pytest.mark.parametrize(
    "endpoint",
    [
        pytest.param(endpoint, id=f"{endpoint.method} {endpoint.path}")
        for endpoint in ENDPOINTS
    ],
)
async def test_limits_every_endpoint(
    client: httpx.AsyncClient, over_the_limit: NonCallableMagicMock, endpoint: Endpoint
):
    url = "/v1" + endpoint.path.format(slug="my-slug", id=ID)

    response = await client.request(endpoint.method, url)

    assert response.status_code == HTTPStatus.TOO_MANY_REQUESTS


async def test_limits_a_request_whose_values_cannot_be_read(
    client: httpx.AsyncClient, over_the_limit: NonCallableMagicMock
):
    response = await client.get("/v1/shorturls/not-a-uuid")
    assert response.status_code == HTTPStatus.TOO_MANY_REQUESTS


@pytest.mark.parametrize("url", ["/openapi.json", "/docs", "/redoc"])
async def test_does_not_limit_the_documentation(
    client: httpx.AsyncClient, over_the_limit: NonCallableMagicMock, url: str
):
    response = await client.get(url)

    assert response.status_code == HTTPStatus.OK
    over_the_limit.hit.assert_not_called()


async def test_does_not_limit_a_request_without_the_address_of_its_client(
    app: FastAPI,
    over_the_limit: NonCallableMagicMock,
    resolve_slug: NonCallableMagicMock,
):
    async with client_from(app, None) as client:
        response = await client.get(RESOLVE_URL)

    assert response.status_code == HTTPStatus.OK
    over_the_limit.hit.assert_not_called()
