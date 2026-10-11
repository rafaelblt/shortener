from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from shortener.domain import ShortURL


@dataclass(frozen=True)
class ShortURLDetails:
    id: UUID
    slug: str
    target_url: str
    owner_id: UUID
    status: str
    resolution_count: int
    created_at: datetime
    last_resolved_at: datetime | None

    @classmethod
    def from_entity(cls, shorturl: ShortURL) -> "ShortURLDetails":
        # Slug and TargetURL are str subclasses, and str() turns them into
        # plain strings, so the details only hold primitives.
        return cls(
            id=shorturl.id.value,
            slug=str(shorturl.slug),
            target_url=str(shorturl.target_url),
            owner_id=shorturl.owner_id.value,
            status=shorturl.status.value,
            resolution_count=shorturl.resolution_count,
            created_at=shorturl.created_at,
            last_resolved_at=shorturl.last_resolved_at,
        )
