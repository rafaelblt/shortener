import asyncio

from pathlib import Path
from typing import Final

from alembic import command
from alembic.config import Config
from alembic.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy import Connection
from sqlalchemy.ext.asyncio import AsyncEngine


MIGRATIONS: Final = Path(__file__).parents[3] / "alembic"
# The key of the advisory lock alembic/env.py takes to migrate. Any number
# does, as long as it is always the same.
MIGRATIONS_LOCK_KEY: Final = 7_364_155_810_201_543_018


class UnexpectedMigrationsError(Exception):
    """The database doesn't have exactly the migrations of the code."""

    def __init__(self, applied: tuple[str, ...], expected: tuple[str, ...]):
        super().__init__(
            f"The database has {_migrations(applied)}, "
            f"and the code expects {_migrations(expected)}"
        )
        self.applied = applied
        self.expected = expected


async def apply_migrations(database_url: str) -> None:
    """
    Applies the migrations the database doesn't have yet, after any other
    process that is applying them. See docs/architecture/infra.md#migrations
    """
    config = _config()
    config.attributes["database_url"] = database_url
    # alembic/env.py runs the migrations in an event loop of its own, which
    # can't run in the one of the caller.
    await asyncio.to_thread(command.upgrade, config, "head")


async def check_migrations(engine: AsyncEngine) -> None:
    """
    Raises:
        UnexpectedMigrationsError: The last migration the database has isn't
            the last one of the code, either behind it or one the code
            doesn't know.
    """
    async with engine.connect() as connection:
        applied = await connection.run_sync(_applied_migrations)
    expected = ScriptDirectory.from_config(_config()).get_heads()
    if set(applied) != set(expected):
        raise UnexpectedMigrationsError(tuple(applied), tuple(expected))


def _applied_migrations(connection: Connection) -> tuple[str, ...]:
    return MigrationContext.configure(connection).get_current_heads()


def _migrations(identifiers: tuple[str, ...]) -> str:
    if not identifiers:
        return "no migrations"
    return f"the migrations {', '.join(identifiers)}"


def _config() -> Config:
    config = Config()
    config.set_main_option("script_location", str(MIGRATIONS))
    return config
