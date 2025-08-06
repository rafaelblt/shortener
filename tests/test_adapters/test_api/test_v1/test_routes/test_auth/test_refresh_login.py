import pytest

from http import HTTPStatus

from fastapi.testclient import TestClient

from shortener.adapters.api.v1.error_codes import ApiErrorCode
from shortener.domain.refresh_token import RefreshToken
from shortener.domain.user.user import User
from shortener.infra.services.jwt_token import JwtTokenService

from tests.utils.entity_helpers import get_persistent_refresh_Token


@pytest.fixture
def route(auth_route):
    return f"{auth_route}/refresh-login/"


def test_response_unprocessable_entity_without_token(
    client: TestClient, route: str
):
    response = client.post(route)
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_response_unauthorized_with_invalid_token(
    client: TestClient, route: str
):
    response = client.post(
        route, json={"refresh_token": "blablablabla"}
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json()["code"] == ApiErrorCode.INVALID_ITEM


@pytest.mark.asyncio
async def test_response_unauthorized_with_token_expired(
    client: TestClient, route: str, db_session, expired_refresh_token: RefreshToken
):
    await get_persistent_refresh_Token(db_session, expired_refresh_token)
    response = client.post(
        route, json={"refresh_token": expired_refresh_token.token}
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json()["code"] == ApiErrorCode.INVALID_ITEM


@pytest.mark.asyncio
async def test_response_unauthorized_with_token_revoked(
    client: TestClient, route: str, db_session, revoked_refresh_token: RefreshToken
):
    await get_persistent_refresh_Token(db_session, revoked_refresh_token)
    response = client.post(
        route, json={"refresh_token": revoked_refresh_token.token}
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json()["code"] == ApiErrorCode.INVALID_ITEM


@pytest.mark.asyncio
async def test_response_forbidden_with_user_banned(
    client: TestClient,
    route: str,
    db_session,
    active_refresh_token: RefreshToken,
    banned_user: User
):
    active_refresh_token._user = banned_user
    await get_persistent_refresh_Token(db_session, active_refresh_token)
    response = client.post(
        route, json={"refresh_token": active_refresh_token.token}
    )
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json()["code"] == ApiErrorCode.ITEM_NOT_ALLOWED


@pytest.mark.asyncio
async def test_response_ok_with_valid_token(
    client: TestClient, route: str, db_session, active_refresh_token: RefreshToken
):
    await get_persistent_refresh_Token(db_session, active_refresh_token)
    response = client.post(
        route, json={"refresh_token": active_refresh_token.token}
    )
    assert response.status_code == HTTPStatus.OK

    json: dict = response.json()

    assert "access_token" in json
    assert "refresh_token" in json
    assert "user" in json

    payload = JwtTokenService().decode_token(json["access_token"]["token"])
    assert payload["subject"] == active_refresh_token.user.email
