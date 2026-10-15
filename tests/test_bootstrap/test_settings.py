import pytest

from collections.abc import Callable
from datetime import timedelta

from shortener.bootstrap.settings import (
    DEFAULT_JWT_LEEWAY,
    AccessTokenSettings,
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
    "JWT_LEEWAY": (lambda settings: settings.access_tokens.leeway, DEFAULT_JWT_LEEWAY),
}
SECONDS = ["JWT_LEEWAY"]


def environment(**changes: str | None) -> dict[str, str]:
    """ENVIRONMENT, with the changes. A change to None removes the variable."""
    return {
        name: value
        for name, value in {**ENVIRONMENT, **changes}.items()
        if value is not None
    }


def test_from_environment_reads_the_settings_from_the_variables():
    assert Settings.from_environment(ENVIRONMENT) == Settings(
        database_url="postgresql+asyncpg://user:password@localhost:5432/shortener",
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


def test_from_environment_reads_a_leeway_of_0():
    settings = Settings.from_environment(environment(JWT_LEEWAY="0"))
    assert settings.access_tokens.leeway == timedelta(0)


def test_from_environment_names_every_problem_at_once():
    with pytest.raises(SettingsError) as raised:
        Settings.from_environment({})
    assert_mentions(str(raised.value), *REQUIRED, "JWT_KEY", "JWT_JWKS_URL")
