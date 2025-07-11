import os
import pytest

from unittest.mock import patch

from shortener.domain.shared.email import Email

from shortener.infra.exceptions import MissingEnvironmentVariableError
from shortener.infra.settings import Settings, ENV_PATTERNS

from tests.settings import TEST_ENV_VARS


@pytest.fixture
def expected_env_vars():
    env_vars = TEST_ENV_VARS
    env_vars.update(Settings._ENV_DEFAULTS)
    return TEST_ENV_VARS


@pytest.fixture
def settings(expected_env_vars: dict[str, str]):
    for key, value in expected_env_vars.items():
        os.environ[key] = value
    return Settings()


def test_attr_env_vars(settings: Settings):
    default_keys = list(Settings._ENV_DEFAULTS.keys())
    required_keys = Settings._REQUIRED_ENV_VARS

    env_vars_keys = list(settings._env_vars.keys())

    for key in default_keys:
        assert key in env_vars_keys
    for key in required_keys:
        assert key in env_vars_keys


def test_env_defaults_in_env_vars(expected_env_vars: dict[str, str]):
    os.environ.update(expected_env_vars) # updating os.environ to be valid
    for key in Settings._ENV_DEFAULTS:
        os.environ.pop(key) # removing default keys to be tested
    
    settings = Settings()
    for var, value in Settings._ENV_DEFAULTS.items():
        assert settings._env_vars[var] == value


def test_init_raises_missing_env_vars():
    missing_vars = Settings._REQUIRED_ENV_VARS
    with patch.dict(os.environ, clear=True):
        with pytest.raises(MissingEnvironmentVariableError) as error:
            Settings()
    assert error.value.var_names == missing_vars


def test_init_with_env_pattern():
    with patch.dict(os.environ, clear=True):
        env_pattern = "development"
        os.environ["ENVIRONMENT_PATTERN"] = env_pattern
        settings = Settings()
        for key, value in ENV_PATTERNS[env_pattern].items():
            assert settings._env_vars[key] == value


def test_property_app_name(settings: Settings, expected_env_vars: dict[str, str]):
    assert settings.APP_NAME == expected_env_vars["APP_NAME"]


def test_property_api_base_url(settings: Settings, expected_env_vars: dict[str, str]):
    assert settings.API_BASE_URL == expected_env_vars["API_BASE_URL"]


def test_property_database_url(settings: Settings, expected_env_vars: dict[str, str]):
    assert settings.DATABASE_URL == expected_env_vars["DATABASE_URL"]


def test_property_alembic_database_url(settings: Settings, expected_env_vars: dict[str, str]):
    assert settings.ALEMBIC_DATABASE_URL == expected_env_vars["ALEMBIC_DATABASE_URL"]


def test_property_jwt_auth_secret_key(settings: Settings, expected_env_vars: dict[str, str]):
    assert settings.JWT_AUTH_SECRET_KEY == expected_env_vars["JWT_AUTH_SECRET_KEY"]


def test_property_jwt_auth_token_algorithm(settings: Settings, expected_env_vars: dict[str, str]):
    expected = expected_env_vars["JWT_AUTH_TOKEN_ALGORITHM"]
    assert settings.JWT_AUTH_TOKEN_ALGORITHM == expected


def test_property_jwt_auth_token_expires_minutes(settings: Settings, expected_env_vars: dict[str, str]):
    expected = int(expected_env_vars["JWT_AUTH_TOKEN_EXPIRES_MINUTES"])
    assert settings.JWT_AUTH_TOKEN_EXPIRES_MINUTES == expected


def test_property_sendgrid_api_key(settings: Settings, expected_env_vars: dict[str, str]):
    assert settings.SENDGRID_API_KEY == expected_env_vars["SENDGRID_API_KEY"]


def test_property_sendgrid_from_email(settings: Settings, expected_env_vars: dict[str, str]):
    expected = Email(expected_env_vars["SENDGRID_FROM_EMAIL"])
    assert settings.SENDGRID_FROM_EMAIL == expected
