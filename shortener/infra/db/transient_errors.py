from collections.abc import Iterator
from contextlib import contextmanager
from typing import Final

from sqlalchemy.exc import DBAPIError
from sqlalchemy.exc import TimeoutError as PoolTimeoutError

from shortener.use_cases.unavailable_error import UnavailableError


# https://www.postgresql.org/docs/current/errcodes-appendix.html
TRANSIENT_SQLSTATE_CLASSES: Final = (
    "08",  # Connection exception
    "53",  # Insufficient resources, such as too many connections
)
TRANSIENT_SQLSTATES: Final = frozenset(
    {
        "40001",  # Serialization failure
        "40P01",  # Deadlock detected
        "55P03",  # Lock not available, such as when lock_timeout runs out
        "57014",  # Query canceled, such as when statement_timeout runs out
        "57P01",  # Admin shutdown
        "57P02",  # Crash shutdown
        "57P03",  # Cannot connect now, such as while the server starts
    }
)


@contextmanager
def unavailable_when_transient() -> Iterator[None]:
    """
    Raises UnavailableError from an error of the database that trying again
    may fix. Any other error goes through as it is.
    See docs/infra.md#failures-of-the-database
    """
    try:
        yield
    except Exception as error:
        if is_transient(error):
            raise UnavailableError() from error
        raise


def is_transient(error: Exception) -> bool:
    # asyncpg raises OSError when it can't reach the server, such as for a
    # refused connection or a timeout, without SQLAlchemy wrapping it.
    if isinstance(error, (OSError, PoolTimeoutError)):
        return True
    if isinstance(error, DBAPIError):
        if error.connection_invalidated:
            return True
        error = error.orig
    sqlstate = getattr(error, "sqlstate", None)
    if not isinstance(sqlstate, str):
        return False
    return (
        sqlstate.startswith(TRANSIENT_SQLSTATE_CLASSES)
        or sqlstate in TRANSIENT_SQLSTATES
    )
