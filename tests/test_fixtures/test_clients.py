import pytest

from fastapi.testclient import TestClient

from shortener.domain.services.token import AuthTokenService
from shortener.domain.user import User

from shortener.infra.dependencies import fastapi_deps

from tests.fixtures.adapters.fastapi_clients import AuthenticatedTestClient


@pytest.fixture
def access_token_service():
    return fastapi_deps.access_token_service.dependency() # type: ignore


def test_client(client, dependency_overrides):
    assert isinstance(client, TestClient)
    assert client.app.dependency_overrides == dependency_overrides # type: ignore


@pytest.mark.asyncio
async def test_normal_user_client(normal_user_client, dependency_overrides):
    assert isinstance(normal_user_client, AuthenticatedTestClient)
    assert normal_user_client.app.dependency_overrides == dependency_overrides # type: ignore


def test_poor_user_client(poor_user_client, dependency_overrides):
    assert isinstance(poor_user_client, AuthenticatedTestClient)
    assert poor_user_client.app.dependency_overrides == dependency_overrides # type: ignore
