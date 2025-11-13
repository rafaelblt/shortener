import pytest

from http import HTTPStatus

from fastapi.testclient import TestClient

from shortener.adapters.api.v1.error_codes import ApiErrorCode
from shortener.infra.services.jwt_token import JwtTokenService

from tests.fixtures.domain.users import UserFixture


@pytest.fixture
def route(auth_route):
    return f"{auth_route}/login/"


def test_validation_of_login_payload(client: TestClient, route: str):
    response = client.post(
        route, json={"email": "invalid", "password": "pAsSs@#$123"}
    )
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_response_unauthorized_with_user_non_existent(client: TestClient, route: str):
    response = client.post(
        route, json={"email": "example@gmail.com", "password": "123"}
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json()["code"] == ApiErrorCode.INVALID_CREDENTIALS


@pytest.mark.asyncio
async def test_response_unauthorized_incorrect_password(
    client: TestClient, route: str, persistent_normal_user: UserFixture
):
    response = client.post(
        route,
        json={
            "email": persistent_normal_user.email,
            "password": "123"
        }
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json()["code"] == ApiErrorCode.INVALID_CREDENTIALS


@pytest.mark.asyncio
async def test_response_forbidden_with_user_banned(
    client: TestClient, route: str, persistent_banned_user: UserFixture
):
    response = client.post(
        route,
        json={
            "email": persistent_banned_user.email,
            "password": persistent_banned_user.mock_data["plain_password"]
        }
    )
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json()["code"] == ApiErrorCode.ITEM_NOT_ALLOWED


@pytest.mark.asyncio
async def test_response_ok_with_valid_login(
    client: TestClient, route: str, persistent_normal_user: UserFixture
):
    response = client.post(
        route,
        json={
            "email": persistent_normal_user.email,
            "password": persistent_normal_user.mock_data["plain_password"]
        }
    )
    assert response.status_code == HTTPStatus.OK

    json: dict = response.json()

    assert "access_token" in json
    assert "refresh_token" in json
    assert "user" in json

    payload = JwtTokenService().decode_token(json["access_token"]["token"])
    assert payload["subject"] == str(json["user"]["id"])
