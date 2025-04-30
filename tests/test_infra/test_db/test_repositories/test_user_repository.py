import pytest
import pytest_asyncio

from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from shortener.domain.shared.pagination import PaginatedResult

from shortener.domain.plan import Plan

from shortener.domain.user import User
from shortener.domain.user.fields import Email, Name, HashedPassword, UserStatus
from shortener.domain.user.exceptions import UserNotFoundInDatabaseError

from shortener.infra.db.repositories import (
    SQLAlchemyPlanRepository, SQLAlchemyUserRepository
)


@pytest_asyncio.fixture
async def repository(sqlalchemy_user_repository):
    return sqlalchemy_user_repository


async def add_plan(session: AsyncSession, plan: Plan):
    plan_repository = SQLAlchemyPlanRepository(session)
    return await plan_repository.add(plan)


async def get_user_with_plan(session: AsyncSession, user: User, plan: Plan = None):
    plan = plan or user.plan
    if plan.id is None:
        plan = await add_plan(session, plan)
    
    user.change_plan(new_plan=plan)
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
    repository: SQLAlchemyUserRepository, normal_user: User
):
    user = await get_user_with_plan(repository.session, normal_user)

    retrieved = await repository.add(user)
    assert isinstance(retrieved, User)
    assert retrieved.id == 1
    assert retrieved.name == normal_user.name


@pytest.mark.asyncio
async def test_get_by_id(
    repository: SQLAlchemyUserRepository, normal_user: User
):
    user = await get_user_with_plan(repository.session, normal_user)
    user = await repository.add(user)

    retrieved = await repository.get_by_id(user.id)

    assert isinstance(retrieved, User)
    assert retrieved.id == user.id
    assert retrieved.name == user.name


@pytest.mark.asyncio
async def test_update(
    repository: SQLAlchemyUserRepository, 
    normal_user: User,
    eco_plan: Plan
):
    user = await get_user_with_plan(repository.session, normal_user)
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


@pytest.mark.asyncio
async def test_update_user_without_id_raises_error(
    repository: SQLAlchemyUserRepository, normal_user: User
):
    user = await get_user_with_plan(repository.session, normal_user)

    with pytest.raises(
        UserNotFoundInDatabaseError, 
        match=f"User with id={user.id} not found in database."
    ):
        await repository.update(user)


@pytest.mark.asyncio
async def test_update_user_non_existent_raises_error(
    repository: SQLAlchemyUserRepository, normal_user: User
):
    user = await get_user_with_plan(repository.session, normal_user)
    user._id = 1

    with pytest.raises(
        UserNotFoundInDatabaseError, 
        match=f"User with id={user.id} not found in database."
    ):
        await repository.update(user)


@pytest.mark.asyncio
async def test_get_all_with_no_users(repository: SQLAlchemyUserRepository):
    retrieved = await repository.get_all()
    assert isinstance(retrieved, list)
    assert len(retrieved) == 0


@pytest.mark.asyncio
async def test_get_all_with_users(
    repository: SQLAlchemyUserRepository, 
    normal_user: User,
    old_user: User
):
    normal_user = await get_user_with_plan(repository.session, normal_user)
    old_user = await get_user_with_plan(repository.session, old_user)

    await repository.add(normal_user)
    await repository.add(old_user)

    retrieved = await repository.get_all()

    assert isinstance(retrieved, list)
    assert len(retrieved) == 2
    for i in range(len(retrieved)):
        expected_id = i + 1
        assert isinstance(retrieved[i], User)
        assert retrieved[i].id == expected_id
    assert retrieved[0].email == normal_user.email
    assert retrieved[1].email == old_user.email


@pytest.mark.asyncio
async def test_get_by_email(
    repository: SQLAlchemyUserRepository, normal_user: User
):
    user = await get_user_with_plan(repository.session, normal_user)
    user = await repository.add(user)

    retrieved = await repository.get_by_email(user.email)
    
    assert isinstance(retrieved, User)
    assert retrieved.id == user.id
    

@pytest.mark.asyncio
async def test_list_paginated(
    repository: SQLAlchemyUserRepository, 
    normal_user: User,
    super_user: User,
    old_user: User,
):
    normal_user = await get_user_with_plan(repository.session, normal_user)
    super_user = await get_user_with_plan(
        repository.session, super_user, normal_user.plan
    )
    old_user = await get_user_with_plan(
        repository.session, old_user, normal_user.plan
    )

    await repository.add(normal_user)
    await repository.add(super_user)
    await repository.add(old_user)

    retrieved = await repository.list_paginated(offset=0, limit=2)

    assert isinstance(retrieved, PaginatedResult)
    assert len(retrieved.items) == 2
    assert retrieved.offset == 0
    assert retrieved.limit == 2
    assert retrieved.total == 3
    assert retrieved.current_page == 1
    for entity in retrieved.items:
        assert isinstance(entity, User)


@pytest.mark.asyncio
async def test_exists_by_email_true(
    repository: SQLAlchemyUserRepository, normal_user: User
):
    user = await get_user_with_plan(repository.session, normal_user)
    user = await repository.add(user)

    retrieved = await repository.exists_by_email(user.email)
    assert retrieved == True


@pytest.mark.asyncio
async def test_exists_by_email_false(
    repository: SQLAlchemyUserRepository, normal_user: User
):
    retrieved = await repository.exists_by_email(normal_user.email)
    assert retrieved == False


@pytest.mark.asyncio
async def test_delete_by_id(
    repository: SQLAlchemyUserRepository, normal_user: User
):
    user = await get_user_with_plan(repository.session, normal_user)
    user = await repository.add(user)

    retrieved = await repository.delete_by_id(user.id)

    assert isinstance(retrieved, User)
    assert retrieved.email == user.email


@pytest.mark.asyncio
async def test_delete_by_id_with_non_existent_id_raises_error(
    repository: SQLAlchemyUserRepository
):
    with pytest.raises(
        UserNotFoundInDatabaseError,
        match=f"User with id=1 not found in database."
    ):
        await repository.delete_by_id(1)
