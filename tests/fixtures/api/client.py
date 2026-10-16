import httpx
import pytest

from collections.abc import AsyncIterator
from unittest.mock import NonCallableMagicMock

from fastapi import FastAPI

from shortener.api.app import create_app
from tests.fixtures.api.doubles import UseCaseDoubles


@pytest.fixture
def app(
    use_cases: UseCaseDoubles,
    access_token_verifier: NonCallableMagicMock,
    rate_limiter: NonCallableMagicMock,
    health_check: NonCallableMagicMock,
) -> FastAPI:
    return create_app(
        use_cases=use_cases,
        access_token_verifier=access_token_verifier,
        rate_limiter=rate_limiter,
        health_check=health_check,
    )


@pytest.fixture
async def client(app: FastAPI) -> AsyncIterator[httpx.AsyncClient]:
    """
    A client of the app. An exception the app doesn't handle becomes its
    500 response, instead of being raised in the test, as a server does.
    """
    transport = httpx.ASGITransport(app=app, raise_app_exceptions=False)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
