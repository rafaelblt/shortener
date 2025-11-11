import pytest
import pytest_asyncio

from contextlib import asynccontextmanager

from fastapi.testclient import TestClient

from shortener.adapters.api.v1.app_factory import create_app
from shortener.domain.user import User

from shortener.infra.db.session import get_session
from shortener.infra.dependencies.fastapi.services.access_token import make_jwt_access_auth_token_service
from shortener.infra.dependencies.fastapi.services.send_email import make_sendgrid_email_service
from shortener.infra.dependencies.fastapi.services.password_hasher import make_passlib_password_hasher_service


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


@pytest.fixture
def dependency_overrides(
    sqlalchemy_session, mock_send_email_service, wrapper_passlib_password_hasher
):
    return {
        get_session: lambda: sqlalchemy_session,
        make_sendgrid_email_service: lambda: mock_send_email_service,
        make_passlib_password_hasher_service: lambda: wrapper_passlib_password_hasher
    }


@asynccontextmanager
async def get_authenticated_client(user: User, dependency_overrides: dict = {}):
    app = create_app(dependency_overrides=dependency_overrides)
    token_service = make_jwt_access_auth_token_service(user_repository=None)
    access_token = await token_service.generate_token(user)

    with AuthenticatedTestClient(app, access_token.value) as client:
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
def client(dependency_overrides: dict):
    app = create_app(dependency_overrides=dependency_overrides)

    with TestClient(app) as client:
        yield client
    
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def normal_user_client(dependency_overrides: dict, persistent_normal_user: User):
    async with get_authenticated_client(persistent_normal_user, dependency_overrides) as client:
        yield client


@pytest_asyncio.fixture
async def poor_user_client(dependency_overrides: dict, persistent_poor_user: User):
    async with get_authenticated_client(persistent_poor_user, dependency_overrides) as client:
        yield client
