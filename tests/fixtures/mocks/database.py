from abc import ABC, abstractmethod
from typing import Any

from shortener.domain.shared.primarykey import PrimaryKey


class IndexManager(ABC):
    @abstractmethod
    def generate_index(self) -> Any:
        pass

    @abstractmethod
    def validate_index(self, index) -> str:
        pass


class IdManager(IndexManager):
    def __init__(self):
        self.id_counter = 0

    def generate_index(self):
        self.id_counter += 1
        return self.id_counter
    
    def validate_index(self, index):
        if not isinstance(index, int):
            raise TypeError("index must be int.")
        return str(index)
        

class PkManager(IndexManager):
    def __init__(self):
        self._id_manager = IdManager()

    def generate_index(self):
        id = self._id_manager.generate_index()
        return PrimaryKey.create_pk_id(id)
    
    def validate_index(self, index):
        if not isinstance(index, PrimaryKey):
            raise TypeError("index must be PrimaryKey.")
        if index.is_undefined():
            raise ValueError("PrimaryKey is undefined.")
        return index.raw_value


class MockDatabase:
    data: dict[str, dict[str, Any]]

    def __init__(self, index_manager: IndexManager):
        self.data = {}
        self._index_manager = index_manager

    def add(self, entity: dict) -> dict:
        index = self._index_manager.generate_index()
        self.insert(index=index, entity=entity)
        return entity

    def insert(self, index, entity: dict):
        self._validate_entity(entity)
        validated_index = self._index_manager.validate_index(index)
        entity["pk"] = index
        self.data[validated_index] = entity

    def get_all(self) -> list[dict]:
        return list(self.data.values())

    def get_by_index(self, index) -> dict[str, Any] | None:
        index = self._index_manager.validate_index(index)
        entities = [entity for idx, entity in self.data.items() if idx == index]
        if len(entities) > 0:
            return entities[0]
        return None
    
    def get_by_field(self, field, value) -> dict | None:
        entities = [
            entity for entity in self.data.values() if entity[field] == value
        ]
        if len(entities) > 0:
            return entities[0]
        return None
    
    def exists_by_index(self, index) -> bool:
        return self.get_by_index(index) is not None

    def delete_by_index(self, index) -> dict | None:
        index = self._index_manager.validate_index(index)
        return self.data.pop(index, None)

    def _validate_entity(self, entity):
        if not isinstance(entity, dict):
            raise TypeError("entity must be a dict.")
