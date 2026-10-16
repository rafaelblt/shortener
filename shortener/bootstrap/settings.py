import os

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import timedelta
from typing import Final
from urllib.parse import urlsplit

from sqlalchemy.engine import make_url
from sqlalchemy.exc import ArgumentError


DATABASE_DRIVER: Final = "postgresql+asyncpg"
RABBITMQ_SCHEMES: Final = ("amqp", "amqps")
# Postgres keeps lock_timeout and statement_timeout in an int of milliseconds.
POSTGRES_MAX_TIMEOUT: Final = timedelta(milliseconds=2**31 - 1)

DEFAULT_DATABASE_POOL_SIZE: Final = 5
DEFAULT_DATABASE_MAX_OVERFLOW: Final = 10
DEFAULT_DATABASE_POOL_TIMEOUT: Final = timedelta(seconds=30)
DEFAULT_DATABASE_CONNECT_TIMEOUT: Final = timedelta(seconds=10)
DEFAULT_DATABASE_LOCK_TIMEOUT: Final = timedelta(seconds=5)
DEFAULT_DATABASE_STATEMENT_TIMEOUT: Final = timedelta(seconds=30)
DEFAULT_JWT_LEEWAY: Final = timedelta(seconds=60)
DEFAULT_JWT_JWKS_TIMEOUT: Final = timedelta(seconds=5)
DEFAULT_RATE_LIMIT_REQUESTS: Final = 60
DEFAULT_RATE_LIMIT_WINDOW: Final = timedelta(seconds=60)


class SettingsError(Exception):
    """The environment variables don't make valid settings."""


@dataclass(frozen=True)
class DatabaseSettings:
    """
    The database, the pool of its connections, and how long the service waits
    for it. See docs/bootstrap.md#settings
    """

    url: str
    pool_size: int = DEFAULT_DATABASE_POOL_SIZE
    max_overflow: int = DEFAULT_DATABASE_MAX_OVERFLOW
    pool_timeout: timedelta = DEFAULT_DATABASE_POOL_TIMEOUT
    connect_timeout: timedelta = DEFAULT_DATABASE_CONNECT_TIMEOUT
    lock_timeout: timedelta = DEFAULT_DATABASE_LOCK_TIMEOUT
    statement_timeout: timedelta = DEFAULT_DATABASE_STATEMENT_TIMEOUT


@dataclass(frozen=True)
class AccessTokenSettings:
    """
    How to verify access tokens. Settings.from_environment() sets exactly one
    of key and jwks_url. See docs/bootstrap.md#settings
    """

    algorithms: tuple[str, ...]
    issuer: str
    audience: str
    key: str | None
    jwks_url: str | None
    leeway: timedelta = DEFAULT_JWT_LEEWAY
    jwks_timeout: timedelta = DEFAULT_JWT_JWKS_TIMEOUT


@dataclass(frozen=True)
class RateLimitSettings:
    """
    How many requests each IP address can make in each window of time.
    See docs/bootstrap.md#settings
    """

    requests: int = DEFAULT_RATE_LIMIT_REQUESTS
    window: timedelta = DEFAULT_RATE_LIMIT_WINDOW


@dataclass(frozen=True)
class Settings:
    database: DatabaseSettings
    access_tokens: AccessTokenSettings
    rate_limit: RateLimitSettings = RateLimitSettings()

    @classmethod
    def from_environment(
        cls, environment: Mapping[str, str] = os.environ
    ) -> "Settings":
        """
        Raises:
            SettingsError: The variables don't make valid settings. Its message
                names every problem.
        """
        variables = _Variables(environment)
        database = _database_settings(variables)
        access_tokens = _access_token_settings(variables)
        rate_limit = _rate_limit_settings(variables)
        if variables.problems:
            raise SettingsError("; ".join(variables.problems))
        return cls(
            database=database, access_tokens=access_tokens, rate_limit=rate_limit
        )


@dataclass(frozen=True)
class ConsumerSettings:
    """
    The settings of the consumer, which has no access tokens or rate limit.
    See docs/bootstrap.md#settings
    """

    database: DatabaseSettings
    rabbitmq_url: str

    @classmethod
    def from_environment(
        cls, environment: Mapping[str, str] = os.environ
    ) -> "ConsumerSettings":
        """
        Raises:
            SettingsError: The variables don't make valid settings. Its message
                names every problem.
        """
        variables = _Variables(environment)
        database = _database_settings(variables)
        rabbitmq_url = _rabbitmq_url(variables)
        if variables.problems:
            raise SettingsError("; ".join(variables.problems))
        return cls(database=database, rabbitmq_url=rabbitmq_url)


def _database_settings(variables: "_Variables") -> DatabaseSettings:
    url = variables.required("DATABASE_URL")
    if url and not _uses_the_driver(url):
        variables.problems.append(f"DATABASE_URL must start with {DATABASE_DRIVER}://")
    return DatabaseSettings(
        url=url,
        pool_size=variables.optional_integer(
            "DATABASE_POOL_SIZE", DEFAULT_DATABASE_POOL_SIZE, minimum=1
        ),
        max_overflow=variables.optional_integer(
            "DATABASE_MAX_OVERFLOW", DEFAULT_DATABASE_MAX_OVERFLOW, minimum=0
        ),
        pool_timeout=variables.optional_seconds(
            "DATABASE_POOL_TIMEOUT", DEFAULT_DATABASE_POOL_TIMEOUT
        ),
        connect_timeout=variables.optional_seconds(
            "DATABASE_CONNECT_TIMEOUT", DEFAULT_DATABASE_CONNECT_TIMEOUT
        ),
        lock_timeout=variables.optional_seconds(
            "DATABASE_LOCK_TIMEOUT",
            DEFAULT_DATABASE_LOCK_TIMEOUT,
            maximum=POSTGRES_MAX_TIMEOUT,
        ),
        statement_timeout=variables.optional_seconds(
            "DATABASE_STATEMENT_TIMEOUT",
            DEFAULT_DATABASE_STATEMENT_TIMEOUT,
            maximum=POSTGRES_MAX_TIMEOUT,
        ),
    )


def _access_token_settings(variables: "_Variables") -> AccessTokenSettings:
    key = variables.optional("JWT_KEY")
    jwks_url = variables.optional("JWT_JWKS_URL")
    if (key is None) == (jwks_url is None):
        variables.problems.append("Set exactly one of JWT_KEY and JWT_JWKS_URL")
    if key is not None and variables.optional("JWT_JWKS_TIMEOUT") is not None:
        variables.problems.append(
            "Set JWT_JWKS_TIMEOUT only with JWT_JWKS_URL, and not with JWT_KEY"
        )
    return AccessTokenSettings(
        algorithms=variables.required_list("JWT_ALGORITHMS"),
        issuer=variables.required("JWT_ISSUER"),
        audience=variables.required("JWT_AUDIENCE"),
        key=key,
        jwks_url=jwks_url,
        leeway=variables.optional_seconds(
            "JWT_LEEWAY", DEFAULT_JWT_LEEWAY, can_be_zero=True
        ),
        jwks_timeout=variables.optional_seconds(
            "JWT_JWKS_TIMEOUT", DEFAULT_JWT_JWKS_TIMEOUT
        ),
    )


def _rabbitmq_url(variables: "_Variables") -> str:
    url = variables.required("RABBITMQ_URL")
    if url and _scheme(url) not in RABBITMQ_SCHEMES:
        variables.problems.append("RABBITMQ_URL must start with amqp:// or amqps://")
    return url


def _rate_limit_settings(variables: "_Variables") -> RateLimitSettings:
    return RateLimitSettings(
        requests=variables.optional_integer(
            "RATE_LIMIT_REQUESTS", DEFAULT_RATE_LIMIT_REQUESTS, minimum=1
        ),
        window=variables.optional_seconds(
            "RATE_LIMIT_WINDOW", DEFAULT_RATE_LIMIT_WINDOW
        ),
    )


class _Variables:
    """Reads the variables, and keeps the problems it finds."""

    def __init__(self, environment: Mapping[str, str]):
        self._environment = environment
        self.problems: list[str] = []

    def required(self, name: str) -> str:
        value = self.optional(name)
        if value is None:
            self.problems.append(f"{name} is missing")
            return ""
        return value

    def required_list(self, name: str) -> tuple[str, ...]:
        """A required variable whose values are separated by commas."""
        values = tuple(
            value.strip()
            for value in (self.optional(name) or "").split(",")
            if value.strip()
        )
        if not values:
            self.problems.append(f"{name} is missing")
        return values

    def optional(self, name: str) -> str | None:
        # An empty variable is the same as one that isn't set.
        value = self._environment.get(name, "").strip()
        return value or None

    def optional_integer(self, name: str, default: int, minimum: int) -> int:
        """An optional variable with a whole number, minimum or more."""
        value = self.optional(name)
        if value is None:
            return default
        number = _integer(value)
        if number is None or number < minimum:
            self.problems.append(f"{name} must be a whole number, {minimum} or more")
            return default
        return number

    def optional_seconds(
        self,
        name: str,
        default: timedelta,
        can_be_zero: bool = False,
        maximum: timedelta = timedelta.max,
    ) -> timedelta:
        """
        An optional variable with a number of seconds, which may have
        decimals: more than 0, or 0 too when it can be zero, and up to
        maximum.
        """
        value = self.optional(name)
        if value is None:
            return default
        seconds = _seconds(value)
        # A microsecond, the resolution of timedelta, is the least time more
        # than 0.
        least = timedelta(0) if can_be_zero else timedelta.resolution
        if seconds is None or not least <= seconds <= maximum:
            requirement = "0 or more" if can_be_zero else "more than 0"
            if maximum < timedelta.max:
                requirement += f", up to {maximum.total_seconds()}"
            self.problems.append(f"{name} must be a number of seconds, {requirement}")
            return default
        return seconds


def _integer(value: str) -> int | None:
    try:
        return int(value)
    except ValueError:
        return None


def _seconds(value: str) -> timedelta | None:
    try:
        return timedelta(seconds=float(value))
    except (ValueError, OverflowError):
        # float() raises ValueError for a value that isn't a number, and
        # timedelta raises it for nan, and OverflowError for inf or a number
        # too large.
        return None


def _scheme(url: str) -> str | None:
    try:
        return urlsplit(url).scheme
    except ValueError:
        # urlsplit raises it for a URL it can't split, such as one with an
        # unclosed bracket in the host.
        return None


def _uses_the_driver(database_url: str) -> bool:
    try:
        return make_url(database_url).drivername == DATABASE_DRIVER
    except ArgumentError:
        return False
