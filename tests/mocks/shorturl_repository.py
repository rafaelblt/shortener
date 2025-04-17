from shortener.domain.shared.pagination import PaginatedResult
from shortener.domain.shorturl import ShortURL, ShortURLRepository
from shortener.domain.shorturl.exceptions import (
    ShortURLInvalidToUpdateError, ShortURLNotFoundInDatabaseError
)


class MockShortURLRepository(ShortURLRepository):
    data: dict[int, dict]

    def __init__(self):
        self.data = {}
        self.id_counter = 0

    async def add(self, shorturl: ShortURL) -> ShortURL:
        shorturl_dict = self._to_dict(shorturl)

        if shorturl_dict["id"] is None:
            shorturl_dict["id"] = self._get_next_id()

        self.data[shorturl_dict["id"]] = shorturl_dict
        
        return self._to_domain(shorturl_dict)
    
    async def update(self, shorturl: ShortURL) -> ShortURL:
        if shorturl.id is None:
            raise ShortURLInvalidToUpdateError("ShortURL needs a ID to update")
        
        if shorturl.id not in self.data:
            raise ShortURLNotFoundInDatabaseError(
                f"ShortURL with id={shorturl.id} not found in MockShortURLRepository."
            )

        shorturl_dict = self.data[shorturl.id]
        shorturl_dict["slug"] = shorturl.slug
        shorturl_dict["original_url"] = shorturl.original_url
        shorturl_dict["status"] = shorturl.status
        shorturl_dict["visit_count"] = shorturl.visit_count
        shorturl_dict["created_at"] = shorturl.created_at
        shorturl_dict["expires_at"] = shorturl.expires_at
        shorturl_dict["last_accessed_at"] = shorturl.last_accessed_at

        return self._to_domain(shorturl_dict)
    
    async def get_all(self) -> list[ShortURL]:
        return [self._to_domain(entity) for entity in self.data.values()]

    async def get_by_id(self, id: int) -> ShortURL | None:
        for id_key in self.data:
            if id_key == id:
                return self._to_domain(self.data[id_key])
        return None

    async def get_by_slug(self, slug: str) -> ShortURL | None:
        for shorturl_dict in self.data.values():
            if shorturl_dict["slug"] == slug:
                return self._to_domain(shorturl_dict)
        return None
    
    async def list_paginated(self, offset, limit):
        total = len(self.data)
        rows = list(self.data.values())[offset:offset + limit]
        entities = [self._to_domain(row) for row in rows]
        return PaginatedResult(entities, total, offset, limit)

    async def exists_by_slug(self, slug: str) -> bool:
        if await self.get_by_slug(slug):
            return True
        return False

    async def delete_by_id(self, id: int) -> ShortURL:
        for id_key in self.data:
            if id_key == id:
                shorturl_dict = self.data.pop(id_key)
                return self._to_domain(shorturl_dict)
        raise ShortURLNotFoundInDatabaseError(
            f"ShortURL with id={id} not found in MockShortURLRepository."
        )
            
    def _to_dict(self, shorturl: ShortURL) ->dict:
        return {
            "id": shorturl.id,
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
            id=shorturl_dict["id"],
            slug=shorturl_dict["slug"],
            original_url=shorturl_dict["original_url"],
            owner=shorturl_dict["owner"],
            status=shorturl_dict["status"],
            visit_count=shorturl_dict["visit_count"],
            created_at=shorturl_dict["created_at"],
            expires_at=shorturl_dict["expires_at"],
            last_accessed_at=shorturl_dict["last_accessed_at"]
        ) 

    def _get_next_id(self):
        self.id_counter += 1
        return self.id_counter