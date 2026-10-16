from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from shortener.infra.db.transient_errors import unavailable_when_transient


class SQLAlchemyHealthCheck:
    """Checks that the database answers. See docs/infra.md#health-check"""

    def __init__(self, engine: AsyncEngine):
        self._engine = engine

    async def check(self) -> None:
        with unavailable_when_transient():
            async with self._engine.connect() as connection:
                await connection.execute(text("SELECT 1"))
