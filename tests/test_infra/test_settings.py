import os
import pytest

from unittest.mock import patch

from shortener.domain.shared.email import Email

from shortener.infra.exceptions import MissingEnvironmentVariableError
from shortener.infra.settings import Settings

from tests.settings import TEST_ENV_VARS


@pytest.fixture
def settings():
    return Settings()


def test_attr_env_vars(settings: Settings):
    default_keys = list(Settings._ENV_DEFAULTS.keys())
    required_keys = Settings._REQUIRED_ENV_VARS
    env_keys = list(settings._env_vars.keys())
    for key in default_keys:
        assert key in env_keys
    for key in required_keys:
        assert key in env_keys


def test_env_defaults_in_env_vars(settings: Settings):
    for var, value in Settings._ENV_DEFAULTS.items():
        assert settings._env_vars[var] == value


def test_init_raises_missing_env_vars():
    missing_vars = Settings._REQUIRED_ENV_VARS
    with patch.dict(os.environ, clear=True):        
        with pytest.raises(MissingEnvironmentVariableError) as error:
            Settings()
    assert error.value.var_names == missing_vars


def test_property_app_name(settings: Settings):
    assert settings.APP_NAME == Settings._ENV_DEFAULTS["APP_NAME"]


def test_property_api_base_url(settings: Settings):
    assert settings.API_BASE_URL == TEST_ENV_VARS["API_BASE_URL"]


def test_property_database_url(settings: Settings):
    assert settings.DATABASE_URL == TEST_ENV_VARS["DATABASE_URL"]


def test_property_alembic_database_url(settings: Settings):
    assert settings.ALEMBIC_DATABASE_URL == TEST_ENV_VARS["ALEMBIC_DATABASE_URL"]


def test_property_jwt_auth_secret_key(settings: Settings):
    assert settings.JWT_AUTH_SECRET_KEY == TEST_ENV_VARS["JWT_AUTH_SECRET_KEY"]


def test_property_jwt_auth_token_algorithm(settings: Settings):
    expected = Settings._ENV_DEFAULTS["JWT_AUTH_TOKEN_ALGORITHM"]
    assert settings.JWT_AUTH_TOKEN_ALGORITHM == expected


def test_property_jwt_auth_token_expires_minutes(settings: Settings):
    expected = int(Settings._ENV_DEFAULTS["JWT_AUTH_TOKEN_EXPIRES_MINUTES"])
    assert settings.JWT_AUTH_TOKEN_EXPIRES_MINUTES == expected


def test_property_sendgrid_api_key(settings: Settings):
    assert settings.SENDGRID_API_KEY == TEST_ENV_VARS["SENDGRID_API_KEY"]


def test_property_sendgrid_from_email(settings: Settings):
    expected = Email(TEST_ENV_VARS["SENDGRID_FROM_EMAIL"])
    assert settings.SENDGRID_FROM_EMAIL == expected
