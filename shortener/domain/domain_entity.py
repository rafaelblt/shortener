from abc import ABC, abstractmethod

from shortener.domain.shared.primarykey import PrimaryKey


class DomainEntity(ABC):
    
    def __init__(self, **kwargs):
        return super().__init__(**kwargs)

    @staticmethod
    @abstractmethod
    def get_fields() -> list[str]:
        pass

    @property
    @abstractmethod
    def pk(self) -> PrimaryKey:
        pass
