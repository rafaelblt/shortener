from shortener.domain.shorturl import ShortURL, ShortURLRepository


class MockShortURLRepository(ShortURLRepository):
    data: list[ShortURL]

    def __init__(self):
        self.data = []

    def save(self, short_url: ShortURL) -> None:
        self.data.append(short_url)

    def exists_by_slug(self, slug: str) -> bool:
        if self.get_by_slug(slug):
            return True
        return False

    def get_by_slug(self, slug: str) -> ShortURL | None:
        for shorturl in self.data:
            if shorturl.slug == slug:
                return shorturl
        return None
