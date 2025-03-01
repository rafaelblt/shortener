from abc import ABC, abstractmethod
from shortener.domain.shorturl import ShortURL


class ShortURLRepository(ABC):

    @abstractmethod
    def save(self, short_url: ShortURL) -> None:
        pass

    @abstractmethod
    def exists_by_slug(self, slug: str) -> bool:
        pass

    @abstractmethod
    def get_by_slug(self, slug: str) -> ShortURL | None:
        pass

    @abstractmethod
    def get_by_id(self, id: int) -> ShortURL | None:
        pass
