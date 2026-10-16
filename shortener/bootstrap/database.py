import math

from datetime import timedelta

from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from shortener.bootstrap.settings import DatabaseSettings


def database_engine(settings: DatabaseSettings) -> AsyncEngine:
    """
    The engine of the database, with the pool and the timeouts of the
    settings. See docs/bootstrap.md#the-database
    """
    # The engine connects only when it is first used, and pre_ping replaces
    # the connections the server closed while they waited in the pool.
    return create_async_engine(
        settings.url,
        pool_pre_ping=True,
        pool_size=settings.pool_size,
        max_overflow=settings.max_overflow,
        pool_timeout=settings.pool_timeout.total_seconds(),
        connect_args={
            "timeout": settings.connect_timeout.total_seconds(),
            "server_settings": {
                "lock_timeout": _milliseconds(settings.lock_timeout),
                "statement_timeout": _milliseconds(settings.statement_timeout),
            },
        },
    )


def _milliseconds(time: timedelta) -> str:
    # Postgres takes these timeouts in whole milliseconds, and 0 turns them
    # off, so a fraction of a millisecond rounds up.
    return f"{math.ceil(time / timedelta(milliseconds=1))}ms"
