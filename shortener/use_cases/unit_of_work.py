from contextlib import AbstractAsyncContextManager
from typing import Protocol

from shortener.use_cases.shorturl_repository import ShortURLRepository


class Transaction(Protocol):
    """
    A short URL read through a transaction can't be changed by another
    transaction until this one ends. See docs/use_cases.md#concurrency
    """

    @property
    def shorturls(self) -> ShortURLRepository: ...

    async def commit(self) -> None: ...


class UnitOfWork(Protocol):
    def begin(self) -> AbstractAsyncContextManager[Transaction]:
        """
        Leaving the block without calling commit(), by a return or an
        exception, rolls the transaction back.
        """
        ...
