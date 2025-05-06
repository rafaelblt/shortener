from shortener.infra.settings import (
    DATABASE_URL,
    ALEMBIC_DATABASE_URL,
    JWT_AUTH_SECRET_KEY,
    JWT_AUTH_TOKEN_ALGORITHM,
    JWT_AUTH_TOKEN_EXPIRES_MINUTES
)


def test_database_url():
    assert isinstance(DATABASE_URL, str)
    assert DATABASE_URL == "sqlite+aiosqlite:///default.db"


def test_alembic_database_url():
    assert isinstance(ALEMBIC_DATABASE_URL, str)
    assert ALEMBIC_DATABASE_URL == "sqlite:///default.db"


def test_jwt_auth_secret_key():
    assert isinstance(JWT_AUTH_SECRET_KEY, str)
    assert JWT_AUTH_SECRET_KEY == "ko@34i!1@!3$!345Aba71"


def test_jwt_auth_token_algorithm():
    assert isinstance(JWT_AUTH_TOKEN_ALGORITHM, str)
    assert JWT_AUTH_TOKEN_ALGORITHM == "HS256"


def test_jwt_auth_token_expires_minutes():
    assert isinstance(JWT_AUTH_TOKEN_EXPIRES_MINUTES, int)
    assert JWT_AUTH_TOKEN_EXPIRES_MINUTES == 60
