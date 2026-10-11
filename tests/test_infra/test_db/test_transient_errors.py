import pytest

from sqlalchemy.exc import DBAPIError
from sqlalchemy.exc import TimeoutError as PoolTimeoutError

from shortener.infra.db.transient_errors import is_transient, unavailable_when_transient
from shortener.use_cases.unavailable_error import UnavailableError


class DriverError(Exception):
    """An error of the driver, with the SQLSTATE the database answered."""

    def __init__(self, sqlstate: str | None):
        super().__init__(sqlstate)
        self.sqlstate = sqlstate


def wrapped(sqlstate: str | None, connection_invalidated: bool = False) -> DBAPIError:
    return DBAPIError(
        "SELECT 1",
        None,
        DriverError(sqlstate),  # type: ignore
        connection_invalidated=connection_invalidated,
    )


@pytest.mark.parametrize(
    "error",
    [
        pytest.param(wrapped("08006"), id="connection failure"),
        pytest.param(wrapped("53300"), id="too many connections"),
        pytest.param(wrapped("40001"), id="serialization failure"),
        pytest.param(wrapped("40P01"), id="deadlock detected"),
        pytest.param(wrapped("55P03"), id="lock not available"),
        pytest.param(wrapped("57014"), id="query canceled"),
        pytest.param(wrapped("57P01"), id="admin shutdown"),
        pytest.param(wrapped("57P02"), id="crash shutdown"),
        pytest.param(wrapped("57P03"), id="cannot connect now"),
        pytest.param(
            wrapped(None, connection_invalidated=True), id="connection invalidated"
        ),
        pytest.param(DriverError("53300"), id="raised by the driver as it is"),
        pytest.param(ConnectionRefusedError(), id="refused connection"),
        pytest.param(TimeoutError(), id="timeout"),
        pytest.param(PoolTimeoutError(), id="no free connection in the pool"),
    ],
)
def test_is_transient_for_a_failure_that_trying_again_may_fix(error: Exception):
    assert is_transient(error)


@pytest.mark.parametrize(
    "error",
    [
        pytest.param(wrapped("42P01"), id="undefined table"),
        pytest.param(wrapped("23505"), id="unique violation"),
        pytest.param(wrapped("28P01"), id="invalid password"),
        pytest.param(wrapped("57P04"), id="database dropped"),
        pytest.param(wrapped(None), id="no SQLSTATE"),
        pytest.param(DriverError("3D000"), id="database that doesn't exist"),
        pytest.param(ValueError(), id="not of the database"),
    ],
)
def test_is_not_transient_for_a_failure_that_trying_again_would_not_fix(
    error: Exception,
):
    assert not is_transient(error)


def test_unavailable_when_transient_raises_unavailable_from_a_transient_error():
    error = wrapped("57014")

    with pytest.raises(UnavailableError) as raised:
        with unavailable_when_transient():
            raise error

    assert raised.value.__cause__ is error


def test_unavailable_when_transient_lets_any_other_error_through():
    error = wrapped("42P01")

    with pytest.raises(DBAPIError) as raised:
        with unavailable_when_transient():
            raise error

    assert raised.value is error
