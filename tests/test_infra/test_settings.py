import os
import pytest
from unittest.mock import patch

from shortener.domain.shared.email import Email

from shortener.infra.exceptions import MissingEnvironmentVariableError
from shortener.infra.settings import Settings


@pytest.fixture
def settings():
    os.putenv("SENDGRID_API_KEY", "apikey")
    os.putenv("SENDGRID_FROM_EMAIL", "from")
    return Settings()


def test_database_url(settings: Settings):
    assert isinstance(settings.DATABASE_URL, str)
    assert settings.DATABASE_URL == "sqlite+aiosqlite:///default.db"


def test_alembic_database_url(settings: Settings):
    assert isinstance(settings.ALEMBIC_DATABASE_URL, str)
    assert settings.ALEMBIC_DATABASE_URL == "sqlite:///default.db"


def test_jwt_auth_secret_key(settings: Settings):
    assert isinstance(settings.JWT_AUTH_SECRET_KEY, str)
    assert settings.JWT_AUTH_SECRET_KEY == "ko@34i!1@!3$!345Aba71"


def test_jwt_auth_token_algorithm(settings: Settings):
    assert isinstance(settings.JWT_AUTH_TOKEN_ALGORITHM, str)
    assert settings.JWT_AUTH_TOKEN_ALGORITHM == "HS256"


def test_jwt_auth_token_expires_minutes(settings: Settings):
    assert isinstance(settings.JWT_AUTH_TOKEN_EXPIRES_MINUTES, int)
    assert settings.JWT_AUTH_TOKEN_EXPIRES_MINUTES == 60


def test_sendgrid_api_key(settings: Settings):
    assert isinstance(settings.SENDGRID_API_KEY, str)
    assert settings.SENDGRID_API_KEY == "apikey"


def test_sendgrid_from_email(settings: Settings):
    assert isinstance(settings.SENDGRID_FROM_EMAIL, Email)
    assert settings.SENDGRID_FROM_EMAIL == "from"


@pytest.mark.parametrize(
    "missing_key", ["SENDGRID_API_KEY", "SENDGRID_FROM_EMAIL"]
)
def test_required_env_missing(missing_key):
    env = {
        "SENDGRID_API_KEY": "SG.fake-api-key",
        "SENDGRID_FROM_EMAIL": "admin@example.com",
    }
    del env[missing_key]

    with patch.dict(os.environ, env, clear=True):
        with pytest.raises(MissingEnvironmentVariableError) as error:
            Settings()
        assert error.value.var_name == missing_key
