from abc import ABC, abstractmethod

from shortener.domain.shared.entity_id import EntityID


class DomainEntity(ABC):
    
    def __init__(self, **kwargs):
        return super().__init__(**kwargs)

    @staticmethod
    @abstractmethod
    def get_fields() -> list[str]:
        pass

    @property
    @abstractmethod
    def id(self) -> EntityID:
        pass
