import pytest

from shortener.domain.shared.pagination import PaginatedResult
from shortener.domain.user import User
from shortener.domain.user.fields import Name
from shortener.domain.user.exceptions import (
    UserInvalidToUpdateError, UserNotFoundInDatabaseError
)

from tests.mocks import MockUserRepository


@pytest.fixture
def repository(mock_user_repository) -> MockUserRepository:
    return mock_user_repository


def test_to_dict(
    repository: MockUserRepository, normal_user: User
):
    user_dict = repository._to_dict(normal_user)
    assert isinstance(user_dict, dict)
    assert user_dict["pk"] == normal_user.id
    assert user_dict["email"] == normal_user.email
    assert user_dict["name"] == normal_user.name
    assert user_dict["hashed_password"] == normal_user.hashed_password
    assert user_dict["plan"] == normal_user.plan
    assert user_dict["shorturls_count"] == normal_user.shorturls_count
    assert user_dict["status"] == normal_user.status
    assert user_dict["is_superuser"] == normal_user.is_superuser
    assert user_dict["created_at"] == normal_user.created_at
    assert user_dict["last_login"] == normal_user.last_login


def test_to_domain(
    repository: MockUserRepository, normal_user: User
):
    user_dict = repository._to_dict(normal_user)
    domain = repository._to_domain(user_dict)
    assert domain.id == user_dict["pk"]
    assert domain.email == user_dict["email"]
    assert domain.name == user_dict["name"]
    assert domain.hashed_password == user_dict["hashed_password"]
    assert domain.plan == user_dict["plan"]
    assert domain.shorturls_count == user_dict["shorturls_count"]
    assert domain.status == user_dict["status"]
    assert domain.is_superuser == user_dict["is_superuser"]
    assert domain.created_at == user_dict["created_at"]
    assert domain.last_login == user_dict["last_login"]


@pytest.mark.asyncio
async def test_add(
    repository: MockUserRepository, normal_user: User
):
    retrieved = await repository.add(normal_user)

    assert isinstance(retrieved, User)
    assert retrieved.id == 1
    assert retrieved.email == normal_user.email

    user_dict = repository.database.get_by_index(1)
    assert user_dict["pk"] == 1
    assert user_dict["email"] == normal_user.email


@pytest.mark.asyncio
async def test_update(
    repository: MockUserRepository, normal_user: User
):
    added = await repository.add(normal_user)
    added.name = Name("New Name")

    retrieved = await repository.update(added)

    assert isinstance(retrieved, User)
    assert retrieved.id == added.id
    assert retrieved.name == "New Name"


@pytest.mark.asyncio
async def test_update_raises_user_invalid_to_update(
    repository: MockUserRepository, normal_user: User
):
    with pytest.raises(
        UserInvalidToUpdateError,
        match="User needs a ID to update"
    ):
        await repository.update(normal_user)


@pytest.mark.asyncio
async def test_update_raises_user_not_found(
    repository: MockUserRepository, normal_user: User
):
    user = await repository.add(normal_user)
    await repository.delete_by_id(user.id)
    with pytest.raises(
        UserNotFoundInDatabaseError,
        match="User with id=1 not found in MockUserRepository."
    ):
        await repository.update(user)


@pytest.mark.asyncio
async def test_get_all_with_no_users(repository: MockUserRepository):
    retrieved = await repository.get_all()
    assert isinstance(retrieved, list)
    assert len(retrieved) == 0


@pytest.mark.asyncio
async def test_get_all_with_users(
    repository: MockUserRepository, 
    normal_user: User,
    super_user: User
):
    await repository.add(normal_user)
    await repository.add(super_user)

    retrieved = await repository.get_all()

    assert isinstance(retrieved, list)
    assert len(retrieved) == 2
    for i in range(len(retrieved)):
        expected_id = i + 1
        assert isinstance(retrieved[i], User)
        assert retrieved[i].id == expected_id
    assert retrieved[0].email == normal_user.email
    assert retrieved[1].email == super_user.email


@pytest.mark.asyncio
async def test_get_by_id(
    repository: MockUserRepository, normal_user: User
):
    await repository.add(normal_user)

    retrieved = await repository.get_by_id(1)

    assert isinstance(retrieved, User)
    assert retrieved.id == 1
    assert retrieved.email == normal_user.email



@pytest.mark.asyncio
async def test_get_by_id_non_existent(repository: MockUserRepository):
    retrieved = await repository.get_by_id(1)
    assert retrieved is None


@pytest.mark.asyncio
async def test_get_by_email(
    repository: MockUserRepository, normal_user: User
):
    await repository.add(normal_user)

    retrieved = await repository.get_by_email(normal_user.email)

    assert isinstance(retrieved, User)
    assert retrieved.id == 1
    assert retrieved.email == normal_user.email


@pytest.mark.asyncio
async def test_get_by_email_non_existent(
    repository: MockUserRepository, normal_user: User
):
    retrieved = await repository.get_by_email(normal_user.email)
    assert retrieved is None


@pytest.mark.asyncio
async def test_list_paginated(
    repository: MockUserRepository, 
    normal_user: User,
    super_user: User,
    old_user: User
):
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
    repository: MockUserRepository, normal_user: User
):
    await repository.add(normal_user)
    assert await repository.exists_by_email(normal_user.email) is True


@pytest.mark.asyncio
async def test_exists_by_email_false(
    repository: MockUserRepository, normal_user: User
):
    assert await repository.exists_by_email(normal_user.email) is False


@pytest.mark.asyncio
async def test_delete_by_id(
    repository: MockUserRepository, normal_user: User
):
    await repository.add(normal_user) 

    deleted = await repository.delete_by_id(1)

    assert isinstance(deleted, User)
    assert deleted.id == 1
    assert deleted.email == normal_user.email
    assert await repository.get_by_id(1) is None


@pytest.mark.asyncio
async def test_delete_by_id_non_existent_user(
    repository: MockUserRepository
):
    with pytest.raises(
        UserNotFoundInDatabaseError,
        match=f"User with id=1 not found in MockUserRepository."
    ):
        await repository.delete_by_id(1)
