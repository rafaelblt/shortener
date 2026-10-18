import asyncio

from pathlib import Path
from typing import Final

from alembic import command
from alembic.config import Config


MIGRATIONS: Final = Path(__file__).parents[3] / "alembic"
# The key of the advisory lock alembic/env.py takes to migrate. Any number
# does, as long as it is always the same.
MIGRATIONS_LOCK_KEY: Final = 7_364_155_810_201_543_018


async def apply_migrations(database_url: str) -> None:
    """
    Applies the migrations the database doesn't have yet, after any other
    process that is applying them. See docs/architecture/infra.md#migrations
    """
    config = Config()
    config.set_main_option("script_location", str(MIGRATIONS))
    config.attributes["database_url"] = database_url
    # alembic/env.py runs the migrations in an event loop of its own, which
    # can't run in the one of the caller.
    await asyncio.to_thread(command.upgrade, config, "head")
