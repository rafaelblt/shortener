import pytest

from http import HTTPStatus

from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from shortener.domain.user import User
from shortener.domain.user.fields import UserStatus

from shortener.infra.db.models import UserModel
from shortener.infra.db.mappers import map_user_model_to_domain
from shortener.infra.services.jwt_auth_token import JwtAuthTokenService

from tests.utils.entity_helpers import get_persistent_user


def test_exception_handler_with_invalid_token(client: TestClient, route: str):
    response = client.get(f"{route}/verify-email?token=invalid-token")
    assert response.status_code == HTTPStatus.BAD_REQUEST


@pytest.mark.asyncio
async def test_success_with_valid_token(
    client: TestClient,
    route: str,
    db_session: AsyncSession,
    unverified_email_user: User
):
    user = await get_persistent_user(db_session, unverified_email_user)

    auth_token = JwtAuthTokenService()
    token = auth_token.generate_token(user.email)
    
    response = client.get(f"{route}/verify-email?token={token}")
    assert response.status_code == HTTPStatus.OK
    assert response.json()["message"] == "Email successfully verified."


@pytest.mark.asyncio
async def test_if_user_status_is_updated(
    client: TestClient,
    route: str,
    db_session: AsyncSession,
    unverified_email_user: User
):
    user = await get_persistent_user(db_session, unverified_email_user)

    auth_token = JwtAuthTokenService()
    token = auth_token.generate_token(user.email)
    
    client.get(f"{route}/verify-email?token={token}")

    updated_user = await db_session.get(UserModel, user.id)
    assert updated_user is not None
    updated_user = map_user_model_to_domain(updated_user)
    assert updated_user.status == UserStatus.ACTIVE
