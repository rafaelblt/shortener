from pydantic import BaseModel
from datetime import datetime

from shortener.domain.shorturl import ShortURL


class PublicShortURLSchema(BaseModel):
    id: int
    slug: str
    original_url: str
    created_at: datetime

    @staticmethod
    def from_domain(shorturl: ShortURL):
        return PublicShortURLSchema(
            id=shorturl.pk.get_id(),
            slug=shorturl.slug,
            original_url=shorturl.original_url,
            created_at=shorturl.created_at
        )
