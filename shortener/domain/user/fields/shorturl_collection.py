from abc import ABC, abstractmethod

from shortener.domain.shared.primarykey import PrimaryKey
from shortener.domain.shorturl import ShortURL
from shortener.domain.shorturl.fields.slug import Slug


class ShortURLCollection(ABC):

    @abstractmethod
    def get_all(self) -> list[ShortURL]: ...

    @abstractmethod
    def get_by_pk(self, pk: PrimaryKey) -> ShortURL | None: ...

    @abstractmethod
    def get_by_slug(self, slug: Slug) -> ShortURL | None: ...

    @abstractmethod
    def add(self, shorturl: ShortURL) -> None: ...

    @abstractmethod
    def remove_by_pk(self, pk: PrimaryKey) -> ShortURL | None: ...
