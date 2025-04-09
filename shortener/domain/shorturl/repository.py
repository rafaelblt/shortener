from abc import ABC, abstractmethod
from shortener.domain.shared import PaginatedResult
from shortener.domain.shorturl import ShortURL


class ShortURLRepository(ABC):

    @abstractmethod
    async def add(self, shorturl: ShortURL) -> ShortURL:
        pass

    @abstractmethod
    async def update(self, shorturl: ShortURL) -> ShortURL:
        pass

    @abstractmethod
    async def get_all(self) -> list[ShortURL]:
        pass

    @abstractmethod
    async def get_by_slug(self, slug: str) -> ShortURL | None:
        pass

    @abstractmethod
    async def get_by_id(self, id: int) -> ShortURL | None:
        pass

    @abstractmethod
    async def list_paginated(self, offset: int, limit: int) -> PaginatedResult[ShortURL]:
        pass

    @abstractmethod
    async def delete_by_id(self, id: int) -> ShortURL:
        pass

    @abstractmethod
    async def exists_by_slug(self, slug: str) -> bool:
        pass
