from shortener.domain.shorturl import ShortURL, ShortURLRepository


class MockShortURLRepository(ShortURLRepository):
    data: dict[int, dict]

    def __init__(self):
        self.data = {}

    async def get_all(self) -> list[ShortURL]:
        return [self._to_domain(entity) for entity in self.data.values()]

    async def save(self, shorturl: ShortURL) -> ShortURL:
        shorturl_dict = self._to_dict(shorturl)

        if shorturl_dict["id"] is None:
            id_counter = 1
            while id_counter in self.data:
                id_counter += 1
            shorturl_dict["id"] = id_counter

        self.data[shorturl_dict["id"]] = shorturl_dict
        
        return self._to_domain(shorturl_dict)

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
    
    async def exists_by_slug(self, slug: str) -> bool:
        if await self.get_by_slug(slug):
            return True
        return False

    async def delete_by_id(self, id: int) -> ShortURL:
        for id_key in self.data:
            if id_key == id:
                shorturl_dict = self.data.pop(id_key)
                return self._to_domain(shorturl_dict)
            
    def _to_dict(self, shorturl: ShortURL) ->dict:
        return {
            "id": shorturl.id,
            "slug": shorturl.slug,
            "original_url": shorturl.original_url,
            "owner_id": shorturl.owner_id,
            "is_active": shorturl.is_active,
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
            owner_id=shorturl_dict["owner_id"],
            is_active=shorturl_dict["is_active"],
            visit_count=shorturl_dict["visit_count"],
            created_at=shorturl_dict["created_at"],
            expires_at=shorturl_dict["expires_at"],
            last_accessed_at=shorturl_dict["last_accessed_at"]
        ) 
