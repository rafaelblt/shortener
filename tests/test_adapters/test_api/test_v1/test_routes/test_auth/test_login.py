import pytest

from http import HTTPStatus

from fastapi.testclient import TestClient

from shortener.domain.user import User
from shortener.domain.user.fields import HashedPassword

from shortener.adapters.api.v1.schemas.auth import LoginResponse

from shortener.infra.services.password_hasher import PasslibPasswordHasher
from shortener.infra.services.jwt_auth_token import JwtAuthTokenService

from tests.utils.entity_helpers import get_persistent_user


def test_validation_of_user_login_schema(client: TestClient, route: str):
    response = client.post(
        f"{route}/login/", json={"email": "invalid", "password": "pAsSs@#$123"}
    )
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert response.json()["detail"][0]["type"] == "invalid_email"


def test_exception_handler_with_non_existent_email(client: TestClient, route: str):
    response = client.post(
        f"{route}/login/", json={"email": "example@gmail.com", "password": "123"}
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json()["detail"] == "Invalid email or password."


@pytest.mark.asyncio
async def test_response_ok_with_valid_login(
    client: TestClient, route: str, db_session, normal_user: User
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

    json: dict = response.json()
    access_token = json.pop("access_token")
    assert json == {
        "token_type": "bearer",
        "expires_minutes": 60,
        "email": normal_user.email
    }
    assert JwtAuthTokenService().decode_token(access_token) == normal_user.email
