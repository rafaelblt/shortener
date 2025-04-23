from abc import ABC, abstractmethod


class IndexManager(ABC):
    @abstractmethod
    def generate_index(self) -> object:
        pass

    def validate_index(self, index) -> None:
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


class MockDatabase:
    data: dict

    def __init__(self, index_manager: IndexManager):
        self.data = {}
        self._index_manager = index_manager

    def add(self, entity: dict) -> dict:
        index = self._index_manager.generate_index()
        self.insert(index=index, entity=entity)
        return entity

    def insert(self, index, entity: dict):
        self._validate_entity(entity)
        self._index_manager.validate_index(index)
        entity["pk"] = index
        self.data[index] = entity

    def get_all(self) -> list[dict]:
        return self.data.values()

    def get_by_index(self, index) -> dict:
        self._index_manager.validate_index(index)
        entities = [entity for idx, entity in self.data.items() if idx == index]
        return entities[0] if len(entities) > 0 else None
    
    def get_by_field(self, field, value) -> dict:
        entities = [
            entity for entity in self.data.values() if entity[field] == value
        ]
        return entities[0] if len(entities) > 0 else None
    
    def exists_by_index(self, index) -> bool:
        return self.get_by_index(index) is not None

    def delete_by_index(self, index) -> dict:
        return self.data.pop(index, None)    


    def _validate_entity(self, entity):
        if not isinstance(entity, dict):
            raise TypeError("entity must be a dict.")
