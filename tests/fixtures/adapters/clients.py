import pytest
import pytest_asyncio

from contextlib import asynccontextmanager

from fastapi.testclient import TestClient

from shortener.adapters.api import app

from shortener.domain.services.token import AuthTokenService
from shortener.domain.user import User

from shortener.infra.dependencies import fastapi_deps


class AuthenticatedTestClient(TestClient):
    def __init__(self, app, access_token: str):
        super().__init__(app)
        self._access_token = access_token

    def request(self, *args, **kwargs):
        if kwargs["headers"] is None:
            kwargs["headers"] = {"Authorization": f"Bearer {self._access_token}"}
        else:
            kwargs["headers"].setdefault("Authorization", f"Bearer {self._access_token}")
        return super().request(*args, **kwargs)


@asynccontextmanager
async def get_authenticated_client(user: User, dependency_overrides: dict = {}):
    token_service: AuthTokenService = fastapi_deps.access_token_service.dependency() # type: ignore
    access_token = await token_service.generate_token(user)

    with AuthenticatedTestClient(app, access_token.value) as client:
        for dependency, override in dependency_overrides.items():
            app.dependency_overrides[dependency] = override
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
def client(dependency_overrides: dict):

    with TestClient(app) as client:
        for dependency, override in dependency_overrides.items():
            app.dependency_overrides[dependency] = override
        yield client

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def normal_user_client(dependency_overrides: dict, persistent_normal_user: User):
    async with get_authenticated_client(persistent_normal_user, dependency_overrides) as client:
        return client


@pytest_asyncio.fixture
async def poor_user_client(dependency_overrides: dict, persistent_poor_user: User):
    async with get_authenticated_client(persistent_poor_user, dependency_overrides) as client:
        return client
