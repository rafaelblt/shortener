from typing import Any

from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext
from sqlalchemy import Connection
from sqlalchemy.ext.asyncio import AsyncEngine

from shortener.infra.db.tables import metadata


def differences_from_the_tables(connection: Connection) -> list[Any]:
    return compare_metadata(MigrationContext.configure(connection), metadata)


async def test_the_migrations_create_the_tables_as_tables_describes_them(
    engine: AsyncEngine,
):
    async with engine.connect() as connection:
        assert await connection.run_sync(differences_from_the_tables) == []
