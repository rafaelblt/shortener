from uuid6 import uuid7

from shortener.domain.entity_id import EntityID


class ShortURLID(EntityID):
    @classmethod
    def generate(cls) -> "ShortURLID":
        return cls(uuid7())
