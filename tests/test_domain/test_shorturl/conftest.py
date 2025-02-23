from pytest import fixture

from shortener.domain.shorturl import ShortURL
from shortener.domain.shorturl.repository import ShortURLRepository


class MockShortURLRepository(ShortURLRepository):
    def save(self, short_url: ShortURL) -> None:
        pass

    def exists_by_slug(self, slug: str) -> bool:
        return True if slug == "joker" else False

    def get_by_slug(self, slug: str) -> ShortURL:
        return None


@fixture
def mock_repository():
    return MockShortURLRepository()
