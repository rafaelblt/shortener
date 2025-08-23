import pytest

from shortener.domain.shared.primarykey import PrimaryKey
from shortener.domain.shorturl.fields.slug import Slug
from shortener.domain.shorturl.shorturl import ShortURL
from shortener.domain.user.fields import ShortURLCollection


class MockShortURLCollection(ShortURLCollection):
    def __init__(self):
        self._items: list[ShortURL] = []

    def get_all(self) -> list[ShortURL]:
        return self._items
    
    def get_by_pk(self, pk: PrimaryKey) -> ShortURL | None:
        if pk.is_undefined():
            return None
        for item in self._items:
            if item.pk.raw_value == pk.raw_value:
                return item
        return None
    
    def get_by_slug(self, slug: Slug) -> ShortURL | None:
        for item in self._items:
            if item.slug == slug:
                return item
        return None

    def add(self, shorturl: ShortURL) -> None:
        return self._items.append(shorturl)
    
    def remove_by_pk(self, pk: PrimaryKey) -> ShortURL | None:
        if pk.is_undefined():
            return None
        found = None
        position = None
        for i, item in enumerate(self._items):
            if item.pk.raw_value == pk.raw_value:
                found = item
                position = i
        if found and position:
            self._items.pop(position)
            return found
        return None


@pytest.fixture
def mock_shorturl_collection():
    return MockShortURLCollection()
