from shortener.domain.shorturl import ShortURL, ShortURLRepository


class MockShortURLRepository(ShortURLRepository):
    data: list[ShortURL]

    def __init__(self):
        self.data = []

    def save(self, shorturl: ShortURL) -> None:
        self.data.append(shorturl)

    def exists_by_slug(self, slug: str) -> bool:
        if self.get_by_slug(slug):
            return True
        return False

    def get_by_slug(self, slug: str) -> ShortURL | None:
        for shorturl in self.data:
            if shorturl.slug == slug:
                return shorturl
        return None
    
    def get_by_id(self, id: int) -> ShortURL | None:
        for shorturl in self.data:
            if shorturl.id == id:
                return shorturl
        return None
    
    def delete_by_id(self, id: int) -> ShortURL:
        for i, entity in enumerate(self.data):
            if entity.id == id:
                return self.data.pop(i)
