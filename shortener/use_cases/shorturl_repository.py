from dataclasses import dataclass
from typing import Protocol

from shortener.domain import ShortURL, ShortURLID, Slug, UserID
from shortener.shared.result import Result


@dataclass(frozen=True)
class SlugTakenError:
    slug: Slug


class ShortURLReader(Protocol):
    async def get_by_id(self, id: ShortURLID) -> ShortURL | None: ...

    async def get_by_slug(self, slug: Slug) -> ShortURL | None: ...

    async def list_by_owner(self, owner_id: UserID) -> list[ShortURL]: ...


class ShortURLRepository(ShortURLReader, Protocol):
    """
    Only exists as the shorturls of a Transaction, so the use cases can't
    write outside of one. See docs/use_cases.md#reading-and-writing
    """

    async def add(self, shorturl: ShortURL) -> Result[None, SlugTakenError]:
        """
        Returns Err when another short URL has the slug. The conflict doesn't
        make the transaction unusable.
        """
        ...

    async def save(self, shorturl: ShortURL) -> Result[None, SlugTakenError]:
        """
        Stores every field of the short URL. Returns Err when another short
        URL has the slug. The conflict doesn't make the transaction unusable.
        """
        ...

    async def remove(self, shorturl: ShortURL) -> None: ...
