import asyncio
import os

from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool, text
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import create_async_engine

from shortener.infra.db.migrations import MIGRATIONS_LOCK_KEY
from shortener.infra.db.tables import metadata


config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)


def database_url() -> str:
    # Whoever runs the migrations from code, such as apply_migrations(), gives
    # the URL in the attributes of the config, which, unlike its options, take
    # a % as it is. The command line takes it from the environment, like the
    # application. See docs/architecture/infra.md#migrations
    url: str | None = config.attributes.get("database_url")
    return url or os.environ["DATABASE_URL"]


def run_migrations_offline() -> None:
    context.configure(
        url=database_url(),
        target_metadata=metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=metadata)
    with context.begin_transaction():
        # Held until the transaction ends, so a process that waited for it
        # finds the migrations of the one that held it committed.
        connection.execute(
            text("SELECT pg_advisory_xact_lock(:key)"), {"key": MIGRATIONS_LOCK_KEY}
        )
        context.run_migrations()


async def run_async_migrations() -> None:
    engine = create_async_engine(database_url(), poolclass=pool.NullPool)
    async with engine.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await engine.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
