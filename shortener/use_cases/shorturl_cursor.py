from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from shortener.domain import ShortURL


@dataclass(frozen=True)
class ShortURLCursor:
    created_at: datetime
    id: UUID

    @classmethod
    def from_entity(cls, shorturl: ShortURL) -> "ShortURLCursor":
        return cls(created_at=shorturl.created_at, id=shorturl.id.value)
