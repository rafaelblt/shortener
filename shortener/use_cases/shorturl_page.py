from dataclasses import dataclass

from shortener.use_cases.shorturl_cursor import ShortURLCursor
from shortener.use_cases.shorturl_details import ShortURLDetails


@dataclass(frozen=True)
class ShortURLPage:
    items: tuple[ShortURLDetails, ...]
    next_cursor: ShortURLCursor | None
