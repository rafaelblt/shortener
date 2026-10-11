from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine

from shortener.infra.db.shorturl_repository import SQLAlchemyShortURLRepository
from shortener.infra.db.transient_errors import unavailable_when_transient


class SQLAlchemyTransaction:

    def __init__(self, connection: AsyncConnection):
        self._connection = connection
        self.shorturls = SQLAlchemyShortURLRepository(connection)

    async def commit(self) -> None:
        with unavailable_when_transient():
            await self._connection.commit()


class SQLAlchemyUnitOfWork:

    def __init__(self, engine: AsyncEngine):
        self._engine = engine

    @asynccontextmanager
    async def begin(self) -> AsyncIterator[SQLAlchemyTransaction]:
        with unavailable_when_transient():
            connection = await self._engine.connect().start()
        try:
            yield SQLAlchemyTransaction(connection)
        finally:
            # Closing the connection rolls back what wasn't committed.
            await connection.close()
