import pytest
import pytest_asyncio

from datetime import datetime, timezone

from shortener.domain.shared.pagination import PaginatedResult
from shortener.domain.shared.primarykey import PrimaryKey

from shortener.domain.plan import Plan

from shortener.domain.user import User
from shortener.domain.user.fields import Email, Name, HashedPassword, UserStatus
from shortener.domain.user.exceptions import UserNotFoundError

from shortener.infra.db.repositories import SQLAlchemyUserRepository

from tests.utils.entity_helpers import assert_user_fields


@pytest_asyncio.fixture
async def repository(sqlalchemy_user_repository):
    return sqlalchemy_user_repository


@pytest.mark.asyncio
async def test_add(
    repository: SQLAlchemyUserRepository,
    normal_user: User,
    persistent_default_plan: Plan
):
    normal_user.change_plan(persistent_default_plan)

    retrieved = await repository.add(normal_user)

    assert isinstance(retrieved, User)
    assert retrieved.pk.get_id() == 1
    assert_user_fields(retrieved, normal_user, ignore_pk=True)


@pytest.mark.asyncio
async def test_get_by_pk(
    repository: SQLAlchemyUserRepository,
    normal_user: User,
    persistent_default_plan: Plan
):
    normal_user.change_plan(persistent_default_plan)
    saved_user = await repository.add(normal_user)

    retrieved = await repository.get_by_pk(saved_user.pk)

    assert isinstance(retrieved, User)
    assert_user_fields(retrieved, saved_user)


# TODO: improve the test below
@pytest.mark.asyncio
async def test_update(
    repository: SQLAlchemyUserRepository, 
    normal_user: User,
    persistent_default_plan: Plan,
    persistent_eco_plan: Plan
):
    # setup: saving the user
    normal_user.change_plan(persistent_default_plan)
    saved_user = await repository.add(normal_user)

    # updating saved user fields
    saved_user._email = Email("test.updated.email@email.com")
    saved_user.change_name(Name("Test Updated Name"))
    saved_user.change_hashed_password(HashedPassword("test!new@hashed#password"))
    saved_user.change_plan(persistent_eco_plan)
    saved_user._status = UserStatus.SUSPENDED
    saved_user._is_superuser = True
    saved_user._created_at = datetime(3000, month=5, day=29, tzinfo=timezone.utc)
    saved_user._last_login = datetime(3000, month=5, day=29, tzinfo=timezone.utc)

    # executing the update repository method
    retrieved = await repository.update(saved_user)

    # asserting the retrieved result
    assert isinstance(retrieved, User)
    assert_user_fields(retrieved, saved_user)

    # asserting the saved user in repository
    updated_user = await repository.get_by_pk(saved_user.pk)
    assert isinstance(updated_user, User)
    assert_user_fields(updated_user, saved_user)


@pytest.mark.asyncio
async def test_update_user_without_id_raises_error(
    repository: SQLAlchemyUserRepository, normal_user: User
):
    with pytest.raises(ValueError, match="The pk is not of type id"):
        await repository.update(normal_user)


@pytest.mark.asyncio
async def test_update_user_non_existent_raises_error(
    repository: SQLAlchemyUserRepository, normal_user: User
):
    normal_user._pk = PrimaryKey.create_pk_id(1)
    with pytest.raises(UserNotFoundError) as error:
        await repository.update(normal_user)
    assert error.value.value == normal_user.pk
    assert error.value.field == "pk"


@pytest.mark.asyncio
async def test_get_all_with_no_users(repository: SQLAlchemyUserRepository):
    retrieved = await repository.get_all()
    assert isinstance(retrieved, list)
    assert len(retrieved) == 0


@pytest.mark.asyncio
async def test_get_all_with_users(
    repository: SQLAlchemyUserRepository, 
    normal_user: User,
    old_user: User,
    persistent_default_plan: Plan
):
    normal_user.change_plan(persistent_default_plan)
    old_user.change_plan(persistent_default_plan)

    await repository.add(normal_user)
    await repository.add(old_user)

    retrieved = await repository.get_all()

    assert isinstance(retrieved, list)
    assert len(retrieved) == 2
    for i in range(len(retrieved)):
        expected_id = i + 1
        assert isinstance(retrieved[i], User)
        assert retrieved[i].pk.get_id() == expected_id
    assert retrieved[0].email == normal_user.email
    assert retrieved[1].email == old_user.email


@pytest.mark.asyncio
async def test_get_by_email(
    repository: SQLAlchemyUserRepository,
    normal_user: User,
    persistent_default_plan: Plan
):
    normal_user.change_plan(persistent_default_plan)
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
    persistent_default_plan: Plan,
):
    normal_user.change_plan(persistent_default_plan)
    super_user.change_plan(persistent_default_plan)
    old_user.change_plan(persistent_default_plan)

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
    repository: SQLAlchemyUserRepository,
    normal_user: User,
    persistent_default_plan: Plan
):
    normal_user.change_plan(persistent_default_plan)
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
async def test_delete_by_pk(
    repository: SQLAlchemyUserRepository,
    normal_user: User,
    persistent_default_plan: Plan
):
    normal_user.change_plan(persistent_default_plan)
    saved_user = await repository.add(normal_user)

    retrieved = await repository.delete_by_pk(saved_user.pk)

    assert isinstance(retrieved, User)
    assert_user_fields(retrieved, saved_user)


@pytest.mark.asyncio
async def test_delete_by_pk_with_non_existent_id_raises_error(
    repository: SQLAlchemyUserRepository
):
    pk = PrimaryKey.create_pk_id(1)
    with pytest.raises(UserNotFoundError) as error:
        await repository.delete_by_pk(pk)
    assert error.value.value == pk
    assert error.value.field == "pk"
