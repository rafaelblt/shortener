import inspect

from typing import Any, Type, TypedDict

from shortener.domain.domain_entity import DomainEntity
from shortener.domain.shared.pagination import PaginatedResult
from shortener.domain.shared.primarykey import PrimaryKey
from tests.fixtures.mocks.database import MockDatabase, PkManager


class EntityNotFoundError(Exception):
    def __init__(self, value: Any, field: str):
        pass


class RepositoryExceptions(TypedDict):
    entity_not_found: Type[EntityNotFoundError]


class ChameleonMockRepository:
    """
    Dynamic mock repository that adapts to an abstract domain repository interface 
    for testing purposes.

    This repository provides basic operations such as `add`, `update`, `delete`, 
    and others. It also auto-generates methods like `get_by_<field>` and 
    `exists_by_<field>` based on naming conventions.

    The target repository class must define the following attributes:
    - `EntityType`: the `DomainEntity` class associated with the repository.
    - `exceptions`: a dictionary containing custom exception types, such as 
    `entity_not_found`.
    """
    EntityType: Type

    def __init__(self, repository_class: Type):
        self.EntityType = repository_class.EntityType
        self.exceptions: RepositoryExceptions = repository_class.exceptions
        self.ENTITY_FIELDS = self.EntityType.get_fields()
        self.DEFAULT_REPO_METHODS = self._get_default_repo_methods()
        self.database = MockDatabase(index_manager=PkManager())
        self._adapt_repository(repository_class)
        
    def _adapt_repository(self, repository_class: Type):
        methods = inspect.getmembers(repository_class, predicate=inspect.isfunction)
        for name, func in methods:
            if name in self.DEFAULT_REPO_METHODS:
                self._set_method(name, self.DEFAULT_REPO_METHODS[name])
            elif name.startswith("get_by") and not name.endswith("_pk"):
                split_name = name.split("_")
                field_name = "_".join(split_name[2::])
                self._set_method(name, self._make_get_by(field_name))
            elif name.startswith("exists_by"):
                split_name = name.split("_")
                field_name = "_".join(split_name[2::])
                self._set_method(name, self._make_exists_by(field_name))

    def _set_method(self, name: str, func):
        setattr(self, name, func.__get__(self, self.__class__))

    def _get_default_repo_methods(self):
        async def add(self, entity):
            entity_dict = self._to_dict(entity)
            entity_dict = self.database.add(entity=entity_dict)
            return self._to_entity(entity_dict)
        
        async def update(self, entity: DomainEntity) -> DomainEntity:
            entity_dict = self.database.get_by_index(entity.pk)

            if entity_dict is None:
                raise self.exceptions["entity_not_found"](value=entity.pk, field="pk")
            
            for field in self.ENTITY_FIELDS:
                entity_dict[field] = entity.__getattribute__(field)
            
            return self._to_entity(entity_dict)

        async def get_all(self) -> list[DomainEntity]:
            return [self._to_entity(entity) for entity in self.database.get_all()]
        
        async def get_by_pk(self, pk: PrimaryKey) -> DomainEntity | None:
            entity_dict = self.database.get_by_index(pk)
            if entity_dict:
                return self._to_entity(entity_dict)
            return None
        
        async def delete(self, entity: DomainEntity) -> DomainEntity:
            return self._delete_by_pk(entity.pk)

        async def delete_by_pk(self, pk: PrimaryKey) -> DomainEntity:
            return self._delete_by_pk(pk)
        
        async def list_paginated(self, offset, limit):
            data = await self.get_all()
            total = len(data)
            rows = list(data)[offset:offset + limit]
            return PaginatedResult(rows, total, offset, limit)

        return {
            "add": add,
            "update": update,
            "get_all": get_all,
            "get_by_pk": get_by_pk,
            "delete": delete,
            "delete_by_pk": delete_by_pk,
            "list_paginated": list_paginated,
        }
    
    def _get_by_field(self, field: str, value: Any) -> DomainEntity | None:
        entity_dict = self.database.get_by_field(field, value)
        if entity_dict:
            return self._to_entity(entity_dict)
        return None
    
    def _delete_by_pk(self, pk: PrimaryKey) -> DomainEntity:
        entity_dict = self.database.delete_by_index(pk)
        if entity_dict:
            return self._to_entity(entity_dict)
        raise self.exceptions["entity_not_found"](value=pk, field="pk")

    def _make_get_by(self, field_name):
        async def get_by_something(self, value):
            return self._get_by_field(field=field_name, value=value)
        return get_by_something

    def _make_exists_by(self, field_name):
        async def exists_by_something(self, value):
            return self._get_by_field(field=field_name, value=value) is not None
        return exists_by_something
    
    def _to_dict(self, entity: DomainEntity):
        entity_dict = {}
        for field in entity.get_fields():
            entity_dict[field] = entity.__getattribute__(field)
        return entity_dict
    
    def _to_entity(self, entity_dict: dict[str, Any]):
        entity = self.EntityType(**entity_dict)
        return entity
