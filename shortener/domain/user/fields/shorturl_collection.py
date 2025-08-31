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
