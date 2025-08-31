from abc import ABC, abstractmethod

from shortener.domain.shared.primarykey import PrimaryKey
from shortener.domain.shorturl import ShortURL
from shortener.domain.shorturl.fields.slug import Slug


class ShortURLCollection(ABC):

    @abstractmethod
    async def get_all(self) -> list[ShortURL]: ...

    @abstractmethod
    async def get_by_pk(self, pk: PrimaryKey) -> ShortURL | None: ...

    @abstractmethod
    async def get_by_slug(self, slug: Slug) -> ShortURL | None: ...

    @abstractmethod
    async def add(self, shorturl: ShortURL) -> None: ...

    @abstractmethod
    async def remove_by_pk(self, pk: PrimaryKey) -> ShortURL | None: ...

    async def count(self) -> int: ...


class InMemoryShortURLCollection(ShortURLCollection):
    def __init__(self, shorturls: list[ShortURL] | None = None):
        self._shorturls = shorturls or []

    async def get_all(self) -> list[ShortURL]:
        return self._shorturls
    
    async def get_by_pk(self, pk: PrimaryKey) -> ShortURL | None:
        if pk.is_undefined():
            return None
        for item in self._shorturls:
            if item.pk.raw_value == pk.raw_value:
                return item
        return None
    
    async def get_by_slug(self, slug: Slug) -> ShortURL | None:
        for item in self._shorturls:
            if item.slug == slug:
                return item
        return None

    async def add(self, shorturl: ShortURL) -> None:
        return self._shorturls.append(shorturl)
    
    async def remove_by_pk(self, pk: PrimaryKey) -> ShortURL | None:
        if pk.is_undefined():
            return None
        found = None
        position = None
        for i, item in enumerate(self._shorturls):
            if item.pk.raw_value == pk.raw_value:
                found = item
                position = i
        if found and position:
            self._shorturls.pop(position)
            return found
        return None
    
    async def count(self):
        return len(self._shorturls)
