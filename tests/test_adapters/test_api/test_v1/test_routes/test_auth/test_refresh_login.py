import pytest

from datetime import timedelta
from http import HTTPStatus

from fastapi.testclient import TestClient

from shortener.adapters.api.v1.error_codes import ApiErrorCode

from shortener.domain.shared.datetime_utils import utc_now
from shortener.domain.user import User

from shortener.infra.db.models import RefreshTokenModel
from shortener.infra.db.sqlalchemy_uow import SQLAlchemyUnitOfWork
from shortener.infra.services.jwt_token import JwtTokenService


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
    client: TestClient,
    route: str,
    persistent_normal_user: User,
    sqlalchemy_uow: SQLAlchemyUnitOfWork,
):
    token_value = "asduijhfiahoicho1893y2r9871hjscd"
    expired_refresh_token = RefreshTokenModel(
        token=token_value,
        expires_at=utc_now(),
        user_id=persistent_normal_user.pk.get_id()
    )
    async with sqlalchemy_uow.transaction() as uow:
        uow.session.add(expired_refresh_token)
    response = client.post(
        route, json={"refresh_token": expired_refresh_token.token}
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json()["code"] == ApiErrorCode.INVALID_ITEM


@pytest.mark.asyncio
async def test_response_unauthorized_with_token_revoked(
    client: TestClient,
    route: str,
    persistent_normal_user: User,
    sqlalchemy_uow: SQLAlchemyUnitOfWork,
):
    token_value = "9087y1789hy8rj9yj2434rpuo8a"
    revoked_refresh_token = RefreshTokenModel(
        token=token_value,
        revoked=True,
        expires_at=utc_now() + timedelta(days=30),
        user_id=persistent_normal_user.pk.get_id(),
    )
    async with sqlalchemy_uow.transaction() as uow:
        uow.session.add(revoked_refresh_token)
    response = client.post(
        route, json={"refresh_token": revoked_refresh_token.token}
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json()["code"] == ApiErrorCode.INVALID_ITEM


@pytest.mark.asyncio
async def test_response_forbidden_with_banned_user(
    client: TestClient,
    route: str,
    persistent_banned_user: User,
    sqlalchemy_uow: SQLAlchemyUnitOfWork,
):
    token_value = "7810245781h07j45f07814278571834785"
    refresh_token = RefreshTokenModel(
        token=token_value,
        expires_at=utc_now() + timedelta(days=30),
        user_id=persistent_banned_user.pk.get_id()
    )
    async with sqlalchemy_uow.transaction() as uow:
        uow.session.add(refresh_token)
    response = client.post(
        route, json={"refresh_token": refresh_token.token}
    )
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json()["code"] == ApiErrorCode.ITEM_NOT_ALLOWED


@pytest.mark.asyncio
async def test_response_ok_with_valid_token(
    client: TestClient,
    route: str,
    persistent_normal_user: User,
    sqlalchemy_uow: SQLAlchemyUnitOfWork,
):
    token_value = "7810245781h07j45f07814278571834785"
    refresh_token = RefreshTokenModel(
        token=token_value,
        expires_at=utc_now() + timedelta(days=30),
        user_id=persistent_normal_user.pk.get_id()
    )
    async with sqlalchemy_uow.transaction() as uow:
        uow.session.add(refresh_token)
    response = client.post(
        route, json={"refresh_token": refresh_token.token}
    )
    assert response.status_code == HTTPStatus.OK

    json: dict = response.json()

    assert "access_token" in json
    assert "refresh_token" in json
    assert "user" in json

    decoded = JwtTokenService().decode_token(json["access_token"]["token"])
    assert decoded["subject"] == str(refresh_token.get_user().id)
