import pytest

from http import HTTPStatus

from fastapi.testclient import TestClient

from shortener.domain.user.fields import HashedPassword
from shortener.infra.services.password_hasher import PasslibPasswordHasher
from shortener.infra.services.jwt_auth_token import JwtAuthTokenService

from tests.utils.entity_helpers import get_persistent_user


def test_response_without_json_data(client: TestClient, route: str):
    response = client.post(f"{route}/login/", json={})
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    json = response.json()
    assert json["detail"][0]["msg"] == "Field required"


def test_response_without_email(client: TestClient, route: str):
    response = client.post(f"{route}/login/", json={"password": "pAsSs@#$123"})
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    json = response.json()
    assert json["detail"][0]["msg"] == "Field required"


def test_response_without_password(client: TestClient, route: str):
    response = client.post(f"{route}/login/", json={"email": "example@gmail.com"})
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    json = response.json()
    assert json["detail"][0]["msg"] == "Field required"


def test_response_with_invalid_email(client: TestClient, route: str):
    response = client.post(
        f"{route}/login/", json={"email": "invalid", "password": "pAsSs@#$123"}
    )
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    json = response.json()
    assert json["detail"][0]["msg"] == "Value error, The User email is invalid."


def test_response_with_non_existent_email(client: TestClient, route: str):
    response = client.post(
        f"{route}/login/", json={"email": "example@gmail.com", "password": "123"}
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    json = response.json()
    assert json["detail"] == "Invalid email or password."


@pytest.mark.asyncio
async def test_response_with_incorrect_password(
    client: TestClient, route: str, db_session, normal_user
):
    normal_user.change_hashed_password(
        HashedPassword(PasslibPasswordHasher().hash("strong-password"))
    )
    user = await get_persistent_user(db_session, normal_user)

    response = client.post(
        f"{route}/login/", json={"email": user.email, "password": "123"}
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    json = response.json()
    assert json["detail"] == "Invalid email or password."


@pytest.mark.asyncio
async def test_response_with_valid_login(
    client: TestClient, route: str, db_session, normal_user
):
    normal_user.change_hashed_password(
        HashedPassword(PasslibPasswordHasher().hash("strong-password"))
    )
    await get_persistent_user(db_session, normal_user)

    response = client.post(
        f"{route}/login/", 
        json={"email": normal_user.email, "password": "strong-password"}
    )
    assert response.status_code == HTTPStatus.OK
    json = response.json()
    assert json["token_type"] == "bearer"
    assert (
        JwtAuthTokenService().decode_token(json["access_token"]) == 
        normal_user.email
    )
