from typing import Any
import pytest

from shortener.domain.domain_entity import DomainEntity
from shortener.domain.shared.pagination import PaginatedResult
from shortener.domain.shared.primarykey import PrimaryKey
from shortener.domain.user import User
from shortener.domain.user.fields import Name

from tests.fixtures.mocks.mock_repository import MockRepository, EntityNotFoundError


class ExampleEntity(DomainEntity):
    @staticmethod
    def get_fields():
        return [
            "pk", "field1", "field2", "field3"
        ]
    
    def __init__(self, pk: PrimaryKey, field1, field2, field3):
        self._pk = pk
        self.field1 = field1
        self.field2 = field2
        self.field3 = field3
    
    @property
    def pk(self):
        return self._pk


@pytest.fixture
def example_entity():
    return ExampleEntity(
        pk=PrimaryKey.create_pk_undefined(),
        field1="field1",
        field2="field2",
        field3="field3"
    )


@pytest.fixture
def repository():
    return MockRepository(ExampleEntity)


def test_to_dict(repository: MockRepository, example_entity: ExampleEntity):
    user_dict = repository._to_dict(example_entity)
    assert isinstance(user_dict, dict)
    assert user_dict["pk"] == example_entity.pk
    assert user_dict["field1"] == example_entity.field1
    assert user_dict["field2"] == example_entity.field2
    assert user_dict["field3"] == example_entity.field3


def test_to_entity(
    repository: MockRepository, example_entity: ExampleEntity
):
    entity_dict = repository._to_dict(example_entity)
    domain = repository._to_entity(entity_dict)
    assert domain.pk == entity_dict["pk"]
    assert domain.field1 == entity_dict["field1"] # type: ignore
    assert domain.field2 == entity_dict["field2"] # type: ignore
    assert domain.field3 == entity_dict["field3"] # type: ignore
    

@pytest.mark.asyncio
async def test_add(
    repository: MockRepository, example_entity: ExampleEntity
):
    retrieved = await repository.add(example_entity)

    assert isinstance(retrieved, ExampleEntity)
    assert retrieved.pk.get_id() == 1
    assert retrieved.field1 == example_entity.field1
    assert retrieved.field2 == example_entity.field2
    assert retrieved.field3 == example_entity.field3

    user_dict = repository.database.get_by_index(retrieved.pk)
    assert user_dict is not None
    assert user_dict["pk"] == retrieved.pk
    assert user_dict["field1"] == example_entity.field1


@pytest.mark.asyncio
async def test_update(
    repository: MockRepository, example_entity: ExampleEntity
):
    added = await repository.add(example_entity)
    added.field1 = "other_field1" # type: ignore
    added.field2 = "other_field2" # type: ignore
    added.field3 = "other_field3" # type: ignore

    retrieved = await repository.update(added)

    assert isinstance(retrieved, ExampleEntity)
    assert retrieved.pk == added.pk
    assert retrieved.field1 == added.field1 # type: ignore
    assert retrieved.field2 == added.field2 # type: ignore
    assert retrieved.field3 == added.field3 # type: ignore


@pytest.mark.asyncio
async def test_update_raises_entity_not_found(
    repository: MockRepository, example_entity: ExampleEntity
):
    entity = await repository.add(example_entity)
    await repository.delete_by_pk(entity.pk)

    with pytest.raises(EntityNotFoundError) as error:
        await repository.update(entity)
    
    assert error.value.value == entity.pk
    assert error.value.field == "pk"


@pytest.mark.asyncio
async def test_get_all_with_no_entities(repository: MockRepository):
    retrieved = await repository.get_all()
    assert isinstance(retrieved, list)
    assert len(retrieved) == 0


@pytest.mark.asyncio
async def test_get_all_with_users(
    repository: MockRepository, example_entity: ExampleEntity,
):
    entity2 = ExampleEntity(PrimaryKey.create_pk_undefined(), 1, 2, 3)
    entity3 = ExampleEntity(PrimaryKey.create_pk_undefined(), 4, 5, 6)
    entity1 = await repository.add(example_entity)
    entity2 = await repository.add(entity2)
    entity3 = await repository.add(entity3)

    retrieved = await repository.get_all()

    assert isinstance(retrieved, list)
    assert len(retrieved) == 3
    assert retrieved[0].pk == entity1.pk
    assert retrieved[1].pk == entity2.pk
    assert retrieved[2].pk == entity3.pk


@pytest.mark.asyncio
async def test_get_by_pk(
    repository: MockRepository, example_entity: ExampleEntity
):
    new_entity = await repository.add(example_entity)

    retrieved = await repository.get_by_pk(new_entity.pk)

    assert isinstance(retrieved, ExampleEntity)
    assert retrieved.pk == new_entity.pk
    assert retrieved.field1 == example_entity.field1


@pytest.mark.asyncio
async def test_get_by_pk_non_existent(repository: MockRepository):
    retrieved = await repository.get_by_pk(PrimaryKey.create_pk_id(1))
    assert retrieved is None


@pytest.mark.asyncio
async def test_get_by_field(
    repository: MockRepository, example_entity: ExampleEntity
):
    new_entity = await repository.add(example_entity)

    retrieved = await repository.get_by_field(
        field="field1", value=example_entity.field1
    )

    assert isinstance(retrieved, ExampleEntity)
    assert retrieved.pk == new_entity.pk
    assert retrieved.field1 == example_entity.field1


@pytest.mark.asyncio
async def test_get_by_field_non_existent(
    repository: MockRepository, example_entity: ExampleEntity
):
    retrieved = await repository.get_by_field(
        field="field1", value=example_entity.field1
    )
    assert retrieved is None


@pytest.mark.asyncio
async def test_list_paginated(
    repository: MockRepository, example_entity: ExampleEntity
):
    entity2 = ExampleEntity(PrimaryKey.create_pk_undefined(), 1, 2, 3)
    entity3 = ExampleEntity(PrimaryKey.create_pk_undefined(), 4, 5, 6)
    entity1 = await repository.add(example_entity)
    entity2 = await repository.add(entity2)
    entity3 = await repository.add(entity3)

    retrieved = await repository.list_paginated(offset=0, limit=2)

    assert isinstance(retrieved, PaginatedResult)
    assert len(retrieved.items) == 2
    assert retrieved.offset == 0
    assert retrieved.limit == 2
    assert retrieved.total == 3
    assert retrieved.current_page == 1
    for entity in retrieved.items:
        assert isinstance(entity, ExampleEntity)


@pytest.mark.asyncio
async def test_delete_by_pk(
    repository: MockRepository, example_entity: ExampleEntity
):
    added_entity = await repository.add(example_entity)

    deleted = await repository.delete_by_pk(added_entity.pk)

    assert isinstance(deleted, ExampleEntity)
    assert deleted.pk == added_entity.pk
    assert deleted.field1 == example_entity.field1
    assert await repository.get_by_pk(added_entity.pk) is None


@pytest.mark.asyncio
async def test_delete_by_pk_non_existent_user(repository: MockRepository):
    pk = PrimaryKey.create_pk_id(1)
    with pytest.raises(EntityNotFoundError) as error:
        await repository.delete_by_pk(pk)
    assert error.value.value == pk
    assert error.value.field == "pk"
