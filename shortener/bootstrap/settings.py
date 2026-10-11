import os

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Final

from sqlalchemy.engine import make_url
from sqlalchemy.exc import ArgumentError


DATABASE_DRIVER: Final = "postgresql+asyncpg"


class SettingsError(Exception):
    """The environment variables don't make valid settings."""


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


@dataclass(frozen=True)
class Settings:
    database_url: str
    access_tokens: AccessTokenSettings

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
        database_url = variables.required("DATABASE_URL")
        algorithms = variables.required_list("JWT_ALGORITHMS")
        issuer = variables.required("JWT_ISSUER")
        audience = variables.required("JWT_AUDIENCE")
        key = variables.optional("JWT_KEY")
        jwks_url = variables.optional("JWT_JWKS_URL")

        if database_url and not _uses_the_driver(database_url):
            variables.problems.append(
                f"DATABASE_URL must start with {DATABASE_DRIVER}://"
            )
        if (key is None) == (jwks_url is None):
            variables.problems.append("Set exactly one of JWT_KEY and JWT_JWKS_URL")
        if variables.problems:
            raise SettingsError("; ".join(variables.problems))

        return cls(
            database_url=database_url,
            access_tokens=AccessTokenSettings(
                algorithms=algorithms,
                issuer=issuer,
                audience=audience,
                key=key,
                jwks_url=jwks_url,
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


def _uses_the_driver(database_url: str) -> bool:
    try:
        return make_url(database_url).drivername == DATABASE_DRIVER
    except ArgumentError:
        return False
