import pytest
import pytest_asyncio

from datetime import datetime, timezone

from shortener.domain.shared.pagination import PaginatedResult

from shortener.domain.plan import Plan

from shortener.domain.user import User
from shortener.domain.user.fields import Email, Name, HashedPassword, UserStatus
from shortener.domain.user.exceptions import UserNotFoundInDatabaseError

from shortener.infra.db.repositories import SQLAlchemyUserRepository

from tests.utils.entity_helpers import get_persistent_plan, assert_user_fields


@pytest_asyncio.fixture
async def repository(sqlalchemy_user_repository):
    return sqlalchemy_user_repository


@pytest.mark.asyncio
async def test_add(
    repository: SQLAlchemyUserRepository, normal_user: User
):
    saved_plan = await get_persistent_plan(
        session=repository.session, plan=normal_user.plan
    )
    normal_user.change_plan(saved_plan)

    retrieved = await repository.add(normal_user)
    assert isinstance(retrieved, User)
    assert retrieved.id == 1
    assert_user_fields(retrieved, normal_user, ignore_id=True)


@pytest.mark.asyncio
async def test_get_by_id(
    repository: SQLAlchemyUserRepository, normal_user: User
):
    saved_plan = await get_persistent_plan(
        session=repository.session, plan=normal_user.plan
    )
    normal_user.change_plan(saved_plan)
    saved_user = await repository.add(normal_user)

    retrieved = await repository.get_by_id(saved_user.id)

    assert isinstance(retrieved, User)
    assert_user_fields(retrieved, saved_user)


@pytest.mark.asyncio
async def test_update(
    repository: SQLAlchemyUserRepository, 
    normal_user: User,
    eco_plan: Plan
):
    saved_plan = await get_persistent_plan(
        session=repository.session, plan=normal_user.plan
    )
    normal_user.change_plan(saved_plan)

    saved_user = await repository.add(normal_user)

    plan = await get_persistent_plan(session=repository.session, plan=eco_plan)
    saved_user._email = Email("test.updated.email@email.com")
    saved_user._name = Name("Test Updated Name")
    saved_user._hashed_password = HashedPassword("test!new@hashed#password")
    saved_user._plan = plan
    saved_user._status = UserStatus.SUSPENDED
    saved_user._is_superuser = True
    saved_user._created_at = datetime(3000, month=5, day=29, tzinfo=timezone.utc)
    saved_user._last_login = datetime(3000, month=5, day=29, tzinfo=timezone.utc)

    retrieved = await repository.update(saved_user)

    assert isinstance(retrieved, User)
    assert_user_fields(retrieved, saved_user)

    updated_user = await repository.get_by_id(saved_user.id)
    assert isinstance(updated_user, User)
    assert_user_fields(updated_user, saved_user)


@pytest.mark.asyncio
async def test_update_user_without_id_raises_error(
    repository: SQLAlchemyUserRepository, normal_user: User
):
    with pytest.raises(
        UserNotFoundInDatabaseError, 
        match=f"User with id={normal_user.id} not found in database."
    ):
        await repository.update(normal_user)


@pytest.mark.asyncio
async def test_update_user_non_existent_raises_error(
    repository: SQLAlchemyUserRepository, normal_user: User
):
    normal_user._id = 1
    with pytest.raises(
        UserNotFoundInDatabaseError, 
        match=f"User with id={normal_user.id} not found in database."
    ):
        await repository.update(normal_user)


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
    saved_plan = await get_persistent_plan(
        session=repository.session, plan=normal_user.plan
    )
    normal_user.change_plan(saved_plan)
    old_user.change_plan(saved_plan)

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
    saved_plan = await get_persistent_plan(
        session=repository.session, plan=normal_user.plan
    )
    normal_user.change_plan(saved_plan)
    saved_user = await repository.add(normal_user)

    retrieved = await repository.get_by_email(saved_user.email)
    
    assert isinstance(retrieved, User)
    assert_user_fields(retrieved, saved_user)
    

@pytest.mark.asyncio
async def test_list_paginated(
    repository: SQLAlchemyUserRepository, 
    normal_user: User,
    super_user: User,
    old_user: User,
):
    saved_plan = await get_persistent_plan(
        session=repository.session, plan=normal_user.plan
    )
    normal_user.change_plan(saved_plan)
    super_user.change_plan(saved_plan)
    old_user.change_plan(saved_plan)

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
    saved_plan = await get_persistent_plan(
        session=repository.session, plan=normal_user.plan
    )
    normal_user.change_plan(saved_plan)
    saved_user = await repository.add(normal_user)

    retrieved = await repository.exists_by_email(saved_user.email)
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
    saved_plan = await get_persistent_plan(
        session=repository.session, plan=normal_user.plan
    )
    normal_user.change_plan(saved_plan)
    saved_user = await repository.add(normal_user)

    retrieved = await repository.delete_by_id(saved_user.id)

    assert isinstance(retrieved, User)
    assert_user_fields(retrieved, saved_user)


@pytest.mark.asyncio
async def test_delete_by_id_with_non_existent_id_raises_error(
    repository: SQLAlchemyUserRepository
):
    with pytest.raises(
        UserNotFoundInDatabaseError,
        match=f"User with id=1 not found in database."
    ):
        await repository.delete_by_id(1)
