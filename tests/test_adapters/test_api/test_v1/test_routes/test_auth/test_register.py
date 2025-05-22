import pytest

from http import HTTPStatus

from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from shortener.domain.user import User
from shortener.infra.db.models import UserModel
from shortener.infra.db.repositories import SQLAlchemyUserRepository

from tests.utils.entity_helpers import get_persistent_plan


def test_validation_of_user_register_schema(client: TestClient, route: str):
    response = client.post(
        f"{route}/login/", 
        json={
            "email": "invalid_email_value",
            "name": "A Common Name",
            "password": "pass123",
            "plan_id": 1
        }
    )
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert response.json()["detail"][0]["type"] == "invalid_email"


def test_exception_handler_with_plan_id_non_existent(
    client: TestClient, route: str, normal_user: User
):
    response = client.post(
        f"{route}/register/", 
        json={
            "email": normal_user.email,
            "name": normal_user.name,
            "password": "pass123",
            "plan_id": 1
        }
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert (
        response.json()["detail"] == f"There is no plan with the given id: 1."
    )


@pytest.mark.asyncio
async def test_response_created_with_valid_data(
    client: TestClient, route: str, normal_user: User, db_session: AsyncSession
):
    await get_persistent_plan(db_session, normal_user.plan)

    response = client.post(
        f"{route}/register/", 
        json={
            "email": normal_user.email,
            "name": normal_user.name,
            "password": "!@#$Password123",
            "plan_id": 1
        }
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json()["message"] == "User registered successfully."


@pytest.mark.asyncio
async def test_if_user_is_saved_in_session(
    client: TestClient, route: str, normal_user: User, db_session: AsyncSession
):
    await get_persistent_plan(db_session, normal_user.plan)

    client.post(
        f"{route}/register/", 
        json={
            "email": normal_user.email,
            "name": normal_user.name,
            "password": "!@#$Password123",
            "plan_id": 1
        }
    )

    repository = SQLAlchemyUserRepository(db_session)
    user = await repository.get_by_id(1)
    assert user is not None
    assert user.name == normal_user.name
    assert user.email == normal_user.email
    assert user.plan.id == 1
