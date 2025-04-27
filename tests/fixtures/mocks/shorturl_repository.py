from shortener.domain.shared.pagination import PaginatedResult
from shortener.domain.shorturl import ShortURL, ShortURLRepository
from shortener.domain.shorturl.exceptions import (
    ShortURLInvalidToUpdateError, ShortURLNotFoundInDatabaseError
)

from .database import MockDatabase, IdManager


class MockShortURLRepository(ShortURLRepository):
    def __init__(self):
        self.database = MockDatabase(index_manager=IdManager())

    async def add(self, shorturl: ShortURL) -> ShortURL:
        shorturl_dict = self._to_dict(shorturl)
        shorturl_dict = self.database.add(entity=shorturl_dict)
        return self._to_domain(shorturl_dict)
    
    async def update(self, shorturl: ShortURL) -> ShortURL:
        if shorturl.id is None:
            raise ShortURLInvalidToUpdateError("ShortURL needs a ID to update")
        
        if not self.database.exists_by_index(shorturl.id):
            raise ShortURLNotFoundInDatabaseError(
                f"ShortURL with id={shorturl.id} not found in MockShortURLRepository."
            )

        shorturl_dict = self.database.get_by_index(shorturl.id)
        shorturl_dict["slug"] = shorturl.slug
        shorturl_dict["original_url"] = shorturl.original_url
        shorturl_dict["owner"] = shorturl.owner
        shorturl_dict["status"] = shorturl.status
        shorturl_dict["visit_count"] = shorturl.visit_count
        shorturl_dict["created_at"] = shorturl.created_at
        shorturl_dict["expires_at"] = shorturl.expires_at
        shorturl_dict["last_accessed_at"] = shorturl.last_accessed_at

        return self._to_domain(shorturl_dict)
    
    async def get_all(self) -> list[ShortURL]:
        return [self._to_domain(entity) for entity in self.database.get_all()]

    async def get_by_id(self, id: int) -> ShortURL | None:
        shorturl_dict = self.database.get_by_index(id)
        if shorturl_dict:
            return self._to_domain(shorturl_dict)
        return None

    async def get_by_slug(self, slug: str) -> ShortURL | None:
        shorturl_dict = self.database.get_by_field(field="slug", value=slug)
        if shorturl_dict:
            return self._to_domain(shorturl_dict)
        return None
    
    async def list_paginated(self, offset, limit):
        data = await self.get_all()
        total = len(data)
        rows = list(data)[offset:offset + limit]
        return PaginatedResult(rows, total, offset, limit)

    async def exists_by_slug(self, slug: str) -> bool:
        if await self.get_by_slug(slug):
            return True
        return False

    async def delete_by_id(self, id: int) -> ShortURL:
        user_dict = self.database.delete_by_index(id)
        if user_dict:
            return self._to_domain(user_dict)
        raise ShortURLNotFoundInDatabaseError(
            f"ShortURL with id={id} not found in MockShortURLRepository."
        )
            
    def _to_dict(self, shorturl: ShortURL) -> dict:
        return {
            "pk": shorturl.id,
            "slug": shorturl.slug,
            "original_url": shorturl.original_url,
            "owner": shorturl.owner,
            "status": shorturl.status,
            "visit_count": shorturl.visit_count,
            "created_at": shorturl.created_at,
            "expires_at": shorturl.expires_at,
            "last_accessed_at": shorturl.last_accessed_at
        }
    
    def _to_domain(self, shorturl_dict:dict) -> ShortURL:
        return ShortURL(
            id=shorturl_dict["pk"],
            slug=shorturl_dict["slug"],
            original_url=shorturl_dict["original_url"],
            owner=shorturl_dict["owner"],
            status=shorturl_dict["status"],
            visit_count=shorturl_dict["visit_count"],
            created_at=shorturl_dict["created_at"],
            expires_at=shorturl_dict["expires_at"],
            last_accessed_at=shorturl_dict["last_accessed_at"]
        ) 
