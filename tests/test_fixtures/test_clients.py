import pytest

from fastapi.testclient import TestClient

from shortener.domain.services.token import AuthTokenService
from shortener.domain.user import User

from shortener.infra.dependencies import fastapi_deps

from tests.fixtures.adapters.client import AuthenticatedTestClient


@pytest.fixture
def access_token_service():
    return fastapi_deps.access_token_service.dependency() # type: ignore


def test_client(client):
    assert isinstance(client, TestClient)


@pytest.mark.asyncio
async def test_normal_user_client(normal_user_client, normal_user: User, access_token_service: AuthTokenService):
    assert isinstance(normal_user_client, AuthenticatedTestClient)


def test_poor_user_client(poor_user_client):
    assert isinstance(poor_user_client, AuthenticatedTestClient)
