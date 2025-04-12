from typing import Generic, Sequence, TypeVar
from math import ceil

T = TypeVar("T")


class PaginatedResult(Generic[T]):
    def __init__(self, items: Sequence[T], total: int, offset: int, limit: int):
        self.items = items
        self.total = total
        self.offset = offset
        self.limit = limit

    @property
    def current_page(self) -> int:
        return self.offset // self.limit + 1

    @property
    def total_pages(self) -> int:
        return ceil(self.total / self.limit)

    @property
    def has_next(self) -> bool:
        return self.offset + self.limit < self.total

    @property
    def has_previous(self) -> bool:
        return self.offset > 0
    
    def __repr__(self):
        return (f"<PaginatedResult total={self.total} offset={self.offset} "
                f"limit={self.limit} items={self.items}>")
