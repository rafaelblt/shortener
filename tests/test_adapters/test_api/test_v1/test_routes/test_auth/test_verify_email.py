import pytest

from datetime import timedelta
from http import HTTPStatus

from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from shortener.adapters.api.v1.error_codes import ApiErrorCode
from shortener.domain.user import User
from shortener.infra.services.jwt_token import JwtTokenService

from tests.utils.entity_helpers import get_persistent_user


@pytest.fixture
def route(auth_route):
    return f"{auth_route}/verify-email"


def test_response_bad_request_with_invalid_token(
    client: TestClient,
    route: str,
    normal_user: User
):
    token_service = JwtTokenService()
    token = token_service.generate_token(
        subject=normal_user.email,
        purpose=token_service.Purpose.LOGIN,
        expires_in=timedelta(minutes=1)
    )

    response = client.get(route, params={"token": token})

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json()["code"] == ApiErrorCode.INVALID_ITEM


def test_response_bad_request_with_user_non_existent(
    client: TestClient,
    route: str,
    normal_user: User
):
    token_service = JwtTokenService()
    token = token_service.generate_token(
        subject=normal_user.email,
        purpose=token_service.Purpose.EMAIL_VERIFICATION,
        expires_in=timedelta(minutes=1)
    )

    response = client.get(route, params={"token": token})

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json()["code"] == ApiErrorCode.INVALID_ITEM


def test_response_gone_with_token_expired(
    client: TestClient,
    route: str,
    normal_user: User
):
    token_service = JwtTokenService()
    token = token_service.generate_token(
        subject=normal_user.email,
        purpose=token_service.Purpose.EMAIL_VERIFICATION,
        expires_in=timedelta()
    )

    response = client.get(route, params={"token": token})

    assert response.status_code == HTTPStatus.GONE
    assert response.json()["code"] == ApiErrorCode.ITEM_EXPIRED


@pytest.mark.asyncio
async def test_response_conflict_with_user_active(
    client: TestClient,
    route: str,
    db_session: AsyncSession,
    normal_user: User
):
    await get_persistent_user(db_session, normal_user)

    token_service = JwtTokenService()
    token = token_service.generate_token(
        subject=normal_user.email,
        purpose=token_service.Purpose.EMAIL_VERIFICATION,
        expires_in=timedelta(minutes=1)
    )

    response = client.get(route, params={"token": token})

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json()["code"] == ApiErrorCode.ALREADY_PROCESSED


@pytest.mark.asyncio
async def test_response_success_with_valid_token(
    client: TestClient,
    route: str,
    db_session: AsyncSession,
    unverified_email_user: User
):
    user = await get_persistent_user(db_session, unverified_email_user)

    token_service = JwtTokenService()
    token = token_service.generate_token(
        subject=user.email,
        purpose=token_service.Purpose.EMAIL_VERIFICATION,
        expires_in=timedelta(minutes=1)
    )
    
    response = client.get(route, params={"token": token})

    assert response.status_code == HTTPStatus.OK
    assert response.json()["message"] == "Email successfully verified."
