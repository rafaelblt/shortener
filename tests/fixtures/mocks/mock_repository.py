from typing import Type, Any

from shortener.domain.domain_entity import DomainEntity
from shortener.domain.shared.pagination import PaginatedResult
from shortener.domain.shared.primarykey import PrimaryKey

from .database import MockDatabase, PkManager


class EntityNotFoundError(Exception):

    def __init__(self, value: Any, field: str):
        self.value = value
        self.field = field 
        super().__init__(f"Entity with {field}={value} not found.")


class MockRepository():
    def __init__(self, entity_class: Type[DomainEntity]):
        self.ENTITY_CLASS = entity_class
        self.ENTITY_FIELDS = entity_class.get_fields()
        self.database = MockDatabase(index_manager=PkManager())

    async def add(self, entity: DomainEntity) -> DomainEntity:
        self._validate_entity_type(entity)
        entity_dict = self._to_dict(entity)
        entity_dict = self.database.add(entity=entity_dict)
        return self._to_entity(entity_dict)
    
    async def update(self, entity: DomainEntity) -> DomainEntity:
        entity_dict = self.database.get_by_index(entity.pk)

        if entity_dict is None:
            raise EntityNotFoundError(value=entity.pk, field="pk") 
        
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
    
    async def get_by_field(self, field: str, value: Any) -> DomainEntity | None:
        entity_dict = self.database.get_by_field(field, value)
        if entity_dict:
            return self._to_entity(entity_dict)
        return None
    
    async def delete_by_pk(self, pk: PrimaryKey) -> DomainEntity:
        entity_dict = self.database.delete_by_index(pk)
        if entity_dict:
            return self._to_entity(entity_dict)
        raise EntityNotFoundError(value=pk, field="pk")
    
    async def list_paginated(self, offset, limit):
        data = await self.get_all()
        total = len(data)
        rows = list(data)[offset:offset + limit]
        return PaginatedResult(rows, total, offset, limit)

    def _to_dict(self, entity: DomainEntity):
        self._validate_entity_type(entity)
        entity_dict = {}
        for field in self.ENTITY_FIELDS:
            entity_dict[field] = entity.__getattribute__(field)
        return entity_dict
    
    def _to_entity(self, entity_dict: dict[str, Any]):
        entity = self.ENTITY_CLASS(**entity_dict)
        return entity

    def _validate_entity_type(self, entity):
        if not isinstance(entity, self.ENTITY_CLASS):
            raise TypeError(
                f"the entity type must be {self.ENTITY_CLASS}, got {type(entity)}"
            )
        
