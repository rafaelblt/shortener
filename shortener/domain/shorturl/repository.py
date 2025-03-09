from abc import ABC, abstractmethod
from shortener.domain.shorturl import ShortURL


class ShortURLRepository(ABC):

    @abstractmethod
    async def get_all(self) -> list[ShortURL]:
        pass

    @abstractmethod
    async def save(self, shorturl: ShortURL) -> ShortURL:
        pass

    @abstractmethod
    async def exists_by_slug(self, slug: str) -> bool:
        pass

    @abstractmethod
    async def get_by_slug(self, slug: str) -> ShortURL | None:
        pass

    @abstractmethod
    async def get_by_id(self, id: int) -> ShortURL | None:
        pass

    @abstractmethod
    async def delete_by_id(self, id: int) -> ShortURL:
        pass
