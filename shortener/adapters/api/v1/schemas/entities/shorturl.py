from pydantic import BaseModel
from datetime import datetime, timezone

from shortener.domain.shorturl import ShortURL


class PublicShortURLSchema(BaseModel):
    id: int
    slug: str
    original_url: str
    created_at: datetime

    @classmethod
    def from_domain(cls, shorturl: ShortURL):
        return cls(
            id=shorturl.pk.get_id(),
            slug=shorturl.slug,
            original_url=shorturl.original_url,
            created_at=shorturl.created_at
        )
    
    @classmethod
    def get_example(cls):
        return cls(
            id=1,
            slug="example-slug",
            original_url="https://example.com",
            created_at=datetime(year=2002, month=6, day=30, tzinfo=timezone.utc)
        )
    

class ShortURLPrivateSchema(BaseModel):
    id: int
    slug: str
    original_url: str
    owner_id: int
    status: str
    visit_count: int
    created_at: datetime
    expires_at: datetime | None
    last_accessed_at: datetime | None

    @classmethod
    def from_domain(cls, shorturl: ShortURL):
        return cls(
            id=shorturl.pk.get_id(),
            slug=shorturl.slug,
            original_url=shorturl.original_url,
            owner_id=int(shorturl.owner_pk.raw_value),
            status=shorturl.status.value,
            visit_count=shorturl.visit_count,
            created_at=shorturl.created_at,
            expires_at=shorturl.expires_at,
            last_accessed_at=shorturl.last_accessed_at
        )
    
    @classmethod
    def get_example(cls):
        return cls(
            id=1,
            slug="example-slug",
            original_url="https://example.com",
            owner_id=1,
            status="active",
            visit_count=71,
            created_at=datetime(year=2002, month=6, day=30, tzinfo=timezone.utc),
            expires_at=datetime(year=2014, month=7, day=8, tzinfo=timezone.utc),
            last_accessed_at=datetime(year=2013, month=6, day=30, tzinfo=timezone.utc),
        )
