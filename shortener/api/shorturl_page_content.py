from dataclasses import dataclass

from shortener.api.cursors import encode_cursor
from shortener.use_cases.shorturl_details import ShortURLDetails
from shortener.use_cases.shorturl_page import ShortURLPage


@dataclass(frozen=True)
class ShortURLPageContent:
    """A ShortURLPage, with next_cursor as the text a client sends back."""

    items: tuple[ShortURLDetails, ...]
    next_cursor: str | None

    @classmethod
    def from_page(cls, page: ShortURLPage) -> "ShortURLPageContent":
        next_cursor = page.next_cursor
        return cls(
            items=page.items,
            next_cursor=encode_cursor(next_cursor) if next_cursor is not None else None,
        )
