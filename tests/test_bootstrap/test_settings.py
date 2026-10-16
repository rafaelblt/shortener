from collections.abc import Callable
from datetime import timedelta

import pytest

from shortener.bootstrap.settings import (
    DEFAULT_DATABASE_CONNECT_TIMEOUT,
    DEFAULT_DATABASE_LOCK_TIMEOUT,
    DEFAULT_DATABASE_MAX_OVERFLOW,
    DEFAULT_DATABASE_POOL_SIZE,
    DEFAULT_DATABASE_POOL_TIMEOUT,
    DEFAULT_DATABASE_STATEMENT_TIMEOUT,
    DEFAULT_JWT_JWKS_TIMEOUT,
    DEFAULT_JWT_LEEWAY,
    DEFAULT_RATE_LIMIT_REQUESTS,
    DEFAULT_RATE_LIMIT_WINDOW,
    POSTGRES_MAX_TIMEOUT,
    AccessTokenSettings,
    ConsumerSettings,
    DatabaseSettings,
    Settings,
    SettingsError,
)
from tests.utils.text_helpers import assert_mentions


ENVIRONMENT = {
    "DATABASE_URL": "postgresql+asyncpg://user:password@localhost:5432/shortener",
    "JWT_ALGORITHMS": "RS256",
    "JWT_ISSUER": "https://issuer.example.com",
    "JWT_AUDIENCE": "shortener",
    "JWT_JWKS_URL": "https://issuer.example.com/jwks.json",
}
REQUIRED = ["DATABASE_URL", "JWT_ALGORITHMS", "JWT_ISSUER", "JWT_AUDIENCE"]
MISSING = [pytest.param(None, id="unset"), pytest.param(" ", id="empty")]

# How to read the value of each optional variable with a number from the
# settings, and its default.
NUMBERS: dict[str, tuple[Callable[[Settings], object], object]] = {
    "DATABASE_POOL_SIZE": (
        lambda settings: settings.database.pool_size,
        DEFAULT_DATABASE_POOL_SIZE,
    ),
    "DATABASE_MAX_OVERFLOW": (
        lambda settings: settings.database.max_overflow,
        DEFAULT_DATABASE_MAX_OVERFLOW,
    ),
    "DATABASE_POOL_TIMEOUT": (
        lambda settings: settings.database.pool_timeout,
        DEFAULT_DATABASE_POOL_TIMEOUT,
    ),
    "DATABASE_CONNECT_TIMEOUT": (
        lambda settings: settings.database.connect_timeout,
        DEFAULT_DATABASE_CONNECT_TIMEOUT,
    ),
    "DATABASE_LOCK_TIMEOUT": (
        lambda settings: settings.database.lock_timeout,
        DEFAULT_DATABASE_LOCK_TIMEOUT,
    ),
    "DATABASE_STATEMENT_TIMEOUT": (
        lambda settings: settings.database.statement_timeout,
        DEFAULT_DATABASE_STATEMENT_TIMEOUT,
    ),
    "JWT_LEEWAY": (lambda settings: settings.access_tokens.leeway, DEFAULT_JWT_LEEWAY),
    "JWT_JWKS_TIMEOUT": (
        lambda settings: settings.access_tokens.jwks_timeout,
        DEFAULT_JWT_JWKS_TIMEOUT,
    ),
    "RATE_LIMIT_REQUESTS": (
        lambda settings: settings.rate_limit.requests,
        DEFAULT_RATE_LIMIT_REQUESTS,
    ),
    "RATE_LIMIT_WINDOW": (
        lambda settings: settings.rate_limit.window,
        DEFAULT_RATE_LIMIT_WINDOW,
    ),
}
WHOLE_NUMBERS = ["DATABASE_POOL_SIZE", "DATABASE_MAX_OVERFLOW", "RATE_LIMIT_REQUESTS"]
POSTGRES_TIMEOUTS = ["DATABASE_LOCK_TIMEOUT", "DATABASE_STATEMENT_TIMEOUT"]
TIMEOUTS = [
    "DATABASE_POOL_TIMEOUT",
    "DATABASE_CONNECT_TIMEOUT",
    *POSTGRES_TIMEOUTS,
    "JWT_JWKS_TIMEOUT",
]
SECONDS = [*TIMEOUTS, "JWT_LEEWAY", "RATE_LIMIT_WINDOW"]
# The variables that can be 0, and what 0 is read as.
ZEROS = {"DATABASE_MAX_OVERFLOW": 0, "JWT_LEEWAY": timedelta(0)}


def environment(**changes: str | None) -> dict[str, str]:
    """ENVIRONMENT, with the changes. A change to None removes the variable."""
    return {
        name: value
        for name, value in {**ENVIRONMENT, **changes}.items()
        if value is not None
    }


def test_from_environment_reads_the_settings_from_the_variables():
    assert Settings.from_environment(ENVIRONMENT) == Settings(
        database=DatabaseSettings(
            url="postgresql+asyncpg://user:password@localhost:5432/shortener"
        ),
        access_tokens=AccessTokenSettings(
            algorithms=("RS256",),
            issuer="https://issuer.example.com",
            audience="shortener",
            key=None,
            jwks_url="https://issuer.example.com/jwks.json",
        ),
    )


def test_from_environment_reads_a_key_instead_of_a_jwks_url():
    settings = Settings.from_environment(
        environment(JWT_JWKS_URL=None, JWT_KEY="a-secret")
    )

    assert settings.access_tokens.key == "a-secret"
    assert settings.access_tokens.jwks_url is None


def test_from_environment_reads_the_algorithms_separated_by_commas():
    settings = Settings.from_environment(environment(JWT_ALGORITHMS=" RS256, ,ES256 "))
    assert settings.access_tokens.algorithms == ("RS256", "ES256")


@pytest.mark.parametrize("name", REQUIRED)
@pytest.mark.parametrize("value", MISSING)
def test_from_environment_raises_naming_a_required_variable_that_is_missing(
    name: str, value: str | None
):
    with pytest.raises(SettingsError) as raised:
        Settings.from_environment(environment(**{name: value}))
    assert_mentions(str(raised.value), name)


def test_from_environment_raises_for_algorithms_that_are_only_commas():
    with pytest.raises(SettingsError) as raised:
        Settings.from_environment(environment(JWT_ALGORITHMS=" , "))
    assert_mentions(str(raised.value), "JWT_ALGORITHMS")


@pytest.mark.parametrize(
    "changes",
    [
        pytest.param({"JWT_KEY": "a-secret"}, id="both"),
        pytest.param({"JWT_JWKS_URL": None}, id="neither"),
    ],
)
def test_from_environment_raises_unless_exactly_one_of_key_and_jwks_url_is_set(
    changes: dict[str, str | None],
):
    with pytest.raises(SettingsError) as raised:
        Settings.from_environment(environment(**changes))
    assert_mentions(str(raised.value), "JWT_KEY", "JWT_JWKS_URL")


@pytest.mark.parametrize(
    "database_url",
    [
        pytest.param("postgresql://user:password@localhost/shortener", id="no driver"),
        pytest.param(
            "postgresql+psycopg://user:password@localhost/shortener",
            id="another driver",
        ),
        pytest.param("not a url", id="not a URL"),
    ],
)
def test_from_environment_raises_for_a_database_url_without_asyncpg(database_url: str):
    with pytest.raises(SettingsError) as raised:
        Settings.from_environment(environment(DATABASE_URL=database_url))
    assert_mentions(str(raised.value), "DATABASE_URL")


@pytest.mark.parametrize("name", NUMBERS)
@pytest.mark.parametrize("value", MISSING)
def test_from_environment_uses_the_default_of_an_optional_number_that_is_missing(
    name: str, value: str | None
):
    read, default = NUMBERS[name]
    assert read(Settings.from_environment(environment(**{name: value}))) == default


@pytest.mark.parametrize("name", SECONDS)
def test_from_environment_reads_a_number_of_seconds_with_decimals(name: str):
    read, _ = NUMBERS[name]
    settings = Settings.from_environment(environment(**{name: " 0.25 "}))
    assert read(settings) == timedelta(milliseconds=250)


@pytest.mark.parametrize("name", SECONDS)
@pytest.mark.parametrize("value", ["5s", "-0.000001", "nan", "inf", "1e20"])
def test_from_environment_raises_naming_a_number_of_seconds_that_isnt_valid(
    name: str, value: str
):
    with pytest.raises(SettingsError) as raised:
        Settings.from_environment(environment(**{name: value}))
    assert_mentions(str(raised.value), name)


@pytest.mark.parametrize("name", WHOLE_NUMBERS)
def test_from_environment_reads_a_whole_number(name: str):
    read, _ = NUMBERS[name]
    assert read(Settings.from_environment(environment(**{name: " 7 "}))) == 7


@pytest.mark.parametrize("name", WHOLE_NUMBERS)
@pytest.mark.parametrize("value", ["seven", "1.5", "-1"])
def test_from_environment_raises_naming_a_whole_number_that_isnt_valid(
    name: str, value: str
):
    with pytest.raises(SettingsError) as raised:
        Settings.from_environment(environment(**{name: value}))
    assert_mentions(str(raised.value), name)


@pytest.mark.parametrize("name", ZEROS)
def test_from_environment_reads_0_for_a_variable_that_can_be_0(name: str):
    read, _ = NUMBERS[name]
    assert read(Settings.from_environment(environment(**{name: "0"}))) == ZEROS[name]


@pytest.mark.parametrize(
    "name",
    [*TIMEOUTS, "DATABASE_POOL_SIZE", "RATE_LIMIT_REQUESTS", "RATE_LIMIT_WINDOW"],
)
def test_from_environment_raises_naming_a_variable_that_cant_be_0(name: str):
    with pytest.raises(SettingsError) as raised:
        Settings.from_environment(environment(**{name: "0"}))
    assert_mentions(str(raised.value), name)


@pytest.mark.parametrize("name", POSTGRES_TIMEOUTS)
def test_from_environment_reads_the_longest_timeout_postgres_takes(name: str):
    read, _ = NUMBERS[name]
    settings = Settings.from_environment(environment(**{name: "2147483.647"}))
    assert read(settings) == POSTGRES_MAX_TIMEOUT


@pytest.mark.parametrize("name", POSTGRES_TIMEOUTS)
def test_from_environment_raises_naming_a_timeout_longer_than_postgres_takes(
    name: str,
):
    with pytest.raises(SettingsError) as raised:
        Settings.from_environment(environment(**{name: "2147483.648"}))
    assert_mentions(str(raised.value), name)


def test_from_environment_raises_for_a_jwks_timeout_with_a_key():
    with pytest.raises(SettingsError) as raised:
        Settings.from_environment(
            environment(JWT_JWKS_URL=None, JWT_KEY="a-secret", JWT_JWKS_TIMEOUT="5")
        )
    assert_mentions(str(raised.value), "JWT_JWKS_TIMEOUT", "JWT_KEY")


def test_from_environment_names_every_problem_at_once():
    with pytest.raises(SettingsError) as raised:
        Settings.from_environment({})
    assert_mentions(str(raised.value), *REQUIRED, "JWT_KEY", "JWT_JWKS_URL")


CONSUMER_ENVIRONMENT = {
    "DATABASE_URL": "postgresql+asyncpg://user:password@localhost:5432/shortener",
    "RABBITMQ_URL": "amqp://user:password@localhost:5672/",
}


def consumer_environment(**changes: str | None) -> dict[str, str]:
    """CONSUMER_ENVIRONMENT, with the changes, like environment()."""
    return {
        name: value
        for name, value in {**CONSUMER_ENVIRONMENT, **changes}.items()
        if value is not None
    }


def test_consumer_settings_from_environment_reads_the_settings_from_the_variables():
    assert ConsumerSettings.from_environment(CONSUMER_ENVIRONMENT) == ConsumerSettings(
        database=DatabaseSettings(
            url="postgresql+asyncpg://user:password@localhost:5432/shortener"
        ),
        rabbitmq_url="amqp://user:password@localhost:5672/",
    )


def test_consumer_settings_from_environment_reads_the_optional_numbers_of_the_database():
    settings = ConsumerSettings.from_environment(
        consumer_environment(DATABASE_POOL_SIZE="2")
    )
    assert settings.database.pool_size == 2


@pytest.mark.parametrize("name", ["DATABASE_URL", "RABBITMQ_URL"])
@pytest.mark.parametrize("value", MISSING)
def test_consumer_settings_from_environment_raises_naming_a_required_variable_that_is_missing(
    name: str, value: str | None
):
    with pytest.raises(SettingsError) as raised:
        ConsumerSettings.from_environment(consumer_environment(**{name: value}))
    assert_mentions(str(raised.value), name)


def test_consumer_settings_from_environment_reads_an_amqps_url():
    url = "amqps://user:password@rabbitmq.example.com/"
    settings = ConsumerSettings.from_environment(consumer_environment(RABBITMQ_URL=url))
    assert settings.rabbitmq_url == url


@pytest.mark.parametrize(
    "url", ["http://localhost:5672/", "localhost:5672", "amqp://[localhost"]
)
def test_consumer_settings_from_environment_raises_for_a_url_that_is_not_of_amqp(
    url: str,
):
    with pytest.raises(SettingsError) as raised:
        ConsumerSettings.from_environment(consumer_environment(RABBITMQ_URL=url))
    assert_mentions(str(raised.value), "RABBITMQ_URL")
