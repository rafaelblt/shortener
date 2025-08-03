import pytest

from http import HTTPStatus

from fastapi.testclient import TestClient

from shortener.adapters.api.v1.error_codes import ApiErrorCode
from shortener.domain.shared.exceptions import EmailInvalidError

from shortener.domain.user import User

from shortener.infra.services.passlib_hasher import PasslibPasswordHasher
from shortener.infra.services.jwt_token import JwtTokenService

from tests.utils.entity_helpers import get_persistent_user


@pytest.fixture
def route(auth_route):
    return f"{auth_route}/login/"


def test_validation_of_user_login_request(client: TestClient, route: str):
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
    client: TestClient, route: str, db_session, normal_user: User
):
    normal_user.change_hashed_password(
        PasslibPasswordHasher().hash("strong-password")
    )
    await get_persistent_user(db_session, normal_user)

    response = client.post(
        route, json={"email": normal_user.email, "password": "123"}
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json()["code"] == ApiErrorCode.INVALID_CREDENTIALS


@pytest.mark.asyncio
async def test_response_ok_with_valid_login(
    client: TestClient, route: str, db_session, normal_user: User
):
    normal_user.change_hashed_password(
        PasslibPasswordHasher().hash("strong-password")
    )
    await get_persistent_user(db_session, normal_user)

    response = client.post(
        route, json={"email": normal_user.email, "password": "strong-password"}
    )
    assert response.status_code == HTTPStatus.OK

    json: dict = response.json()

    assert "access_token" in json
    assert "refresh_token" in json
    assert "user" in json

    payload = JwtTokenService().decode_token(json["access_token"]["token"])
    assert payload["subject"] == normal_user.email
