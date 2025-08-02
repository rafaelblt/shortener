import pytest

from http import HTTPStatus

from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from shortener.domain.user import User
from shortener.domain.shared.language import Language
from shortener.domain.shared.exceptions import EmailInvalidError
from shortener.infra.db.repositories import SQLAlchemyUserRepository

from tests.fixtures import MockSendEmailService
from tests.fixtures.domain.users import UserFixture
from tests.utils.entity_helpers import get_persistent_plan


@pytest.fixture
def route(auth_route: str):
    return f"{auth_route}/register"


def test_validation_of_user_register_request(client: TestClient, route: str):
    response = client.post(
        route, 
        json={
            "email": "invalid_email_value",
            "name": "A Common Name",
            "password": "pass123",
            "plan_id": 1
        }
    )
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert response.json()["detail"][0]["type"] == EmailInvalidError.code.lower()


@pytest.mark.asyncio
async def test_response_bad_request_with_plan_non_existent(
    client: TestClient, route: str, normal_user: UserFixture
):
    response = client.post(
        route, 
        json={
            "email": normal_user.email,
            "name": normal_user.name,
            "password": normal_user.mock_data["plain_password"],
            "plan_id": 1
        }
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json()["code"] == "PLAN_NOT_FOUND"


@pytest.mark.asyncio
async def test_response_created_with_valid_data(
    client: TestClient, route: str, normal_user: User, db_session: AsyncSession
):
    await get_persistent_plan(db_session, normal_user.plan)
    response = client.post(
        route, 
        json={
            "email": normal_user.email,
            "name": normal_user.name,
            "password": "!@#$Password123",
            "plan_id": 1
        }
    )
    assert response.status_code == HTTPStatus.CREATED

@pytest.mark.asyncio
async def test_if_user_is_saved_in_session(
    client: TestClient, route: str, normal_user: User, db_session: AsyncSession
):
    await get_persistent_plan(db_session, normal_user.plan)
    client.post(
        route,
        json={
            "email": normal_user.email,
            "name": normal_user.name,
            "password": "!@#$Password123",
            "plan_id": 1
        }
    )
    repository = SQLAlchemyUserRepository(db_session)
    user = await repository.get_by_email(normal_user.email)
    assert user is not None
    assert user.name == normal_user.name
    assert user.email == normal_user.email
    assert user.plan.name == normal_user.plan.name


@pytest.mark.asyncio
async def test_if_email_is_sent_to_user(
    client: TestClient, route: str, normal_user: User, db_session: AsyncSession
):
    await get_persistent_plan(db_session, normal_user.plan)
    client.post(
        route,
        headers={"Accept-Language": Language.PT_BR},
        json={
            "email": normal_user.email,
            "name": normal_user.name,
            "password": "!@#$Password123",
            "plan_id": 1
        }
    )
    logs = MockSendEmailService().mock_logs
    assert logs[0]["to"] == normal_user.email
