import pytest
import pytest_asyncio

from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from shortener.domain.plan import Plan

from shortener.domain.user import User
from shortener.domain.user.fields import Email, Name, HashedPassword, UserStatus
from shortener.domain.user.exceptions import (
    UserInvalidToUpdateError
)

from shortener.infra.db.repositories import (
    SQLAlchemyPlanRepository, SQLAlchemyUserRepository
)


@pytest_asyncio.fixture
async def repository(sqlalchemy_user_repository):
    return sqlalchemy_user_repository


async def add_plan(session: AsyncSession, plan: Plan):
    plan_repository = SQLAlchemyPlanRepository(session)
    return await plan_repository.add(plan)


async def get_user_with_plan(session: AsyncSession, user: User, plan: Plan):
    plan_saved = await add_plan(session, plan)
    user.change_plan(new_plan=plan_saved)
    return user


def assert_user_fields(first, second):
    assert first.id == second.id
    assert first.email == second.email
    assert first.name == second.name
    assert first.hashed_password == second.hashed_password
    assert first.plan.id == second.plan.id
    assert first.status == second.status
    assert first.is_superuser == second.is_superuser
    assert first.created_at == second.created_at
    assert first.last_login == second.last_login


@pytest.mark.asyncio
async def test_add(
    repository: SQLAlchemyUserRepository, 
    normal_user: User,
    default_plan: Plan
):
    user = await get_user_with_plan(repository.session, normal_user, default_plan)

    retrieved = await repository.add(user)
    assert isinstance(retrieved, User)
    assert retrieved.id == 1
    assert retrieved.name == normal_user.name


@pytest.mark.asyncio
async def test_get_by_id(
    repository: SQLAlchemyUserRepository, 
    normal_user: User,
    default_plan: Plan
):
    user = await get_user_with_plan(repository.session, normal_user, default_plan)
    user = await repository.add(user)

    retrieved = await repository.get_by_id(user.id)

    assert isinstance(retrieved, User)
    assert retrieved.id == user.id
    assert retrieved.name == user.name


@pytest.mark.asyncio
async def test_update(
    repository: SQLAlchemyUserRepository, 
    normal_user: User,
    default_plan: Plan,
    eco_plan: Plan
):
    user = await get_user_with_plan(repository.session, normal_user, default_plan)
    plan = await add_plan(repository.session, eco_plan)

    user = await repository.add(user)
    user._email = Email("test.updated.email@email.com")
    user._name = Name("Test Updated Name")
    user._hashed_password = HashedPassword("test!new@hashed#password")
    user._plan = plan
    user._status = UserStatus.SUSPENDED
    user._is_superuser = True
    user._created_at = datetime(3000, month=5, day=29, tzinfo=timezone.utc)
    user._last_login = datetime(3000, month=5, day=29, tzinfo=timezone.utc)

    retrieved = await repository.update(user)

    assert isinstance(retrieved, User)
    assert_user_fields(retrieved, user)

    user_saved = await repository.get_by_id(user.id)
    assert isinstance(user_saved, User)
    assert_user_fields(user_saved, user)
