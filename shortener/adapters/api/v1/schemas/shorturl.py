from pydantic import BaseModel
from datetime import datetime
from typing import Optional

from shortener.domain.shorturl import ShortURL
from shortener.domain.shorturl.fields import ShortURLStatus


class ShortURLSchema(BaseModel):
    id: int
    slug: str
    original_url: str
    owner_id: int
    status: ShortURLStatus
    visit_count: int
    created_at: datetime
    expires_at: Optional[datetime]
    last_accessed_at: Optional[datetime]

    @staticmethod
    def from_domain(entity: ShortURL):
        return ShortURLSchema(
            id=entity.id,
            slug=entity.slug,
            original_url=entity.original_url,
            owner_id=entity.owner.id,
            status=entity.status,
            visit_count=entity.visit_count,
            created_at=entity.created_at,
            expires_at=entity.expires_at,
            last_accessed_at=entity.last_accessed_at
        )
