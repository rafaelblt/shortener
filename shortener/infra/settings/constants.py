from shortener.domain.shared.language import Language
from .utils import get_project_app_version


STATIC_SETTINGS = {
    "APP_VERSION": get_project_app_version(),
    "SUPPORTED_LANGUAGES": [Language.EN, Language.PT_BR]
}

REQUIRED_ENV_VARS = [
    "API_BASE_URL",
    "DATABASE_URL",
    "ALEMBIC_DATABASE_URL",
    "JWT_AUTH_SECRET_KEY",
    "SENDGRID_API_KEY",
    "SENDGRID_FROM_EMAIL"
]

OPTIONAL_ENV_VARS = [
    "APP_NAME",
    "JWT_AUTH_TOKEN_ALGORITHM",
    "JWT_AUTH_TOKEN_EXPIRES_MINUTES",
]

ENV_DEFAULTS = {
    "APP_NAME": "Shortener",
    "JWT_AUTH_TOKEN_ALGORITHM": "HS256",
    "JWT_AUTH_TOKEN_EXPIRES_MINUTES": "60",
}

ENV_PATTERNS: dict[str, dict[str, str]] = {
    "development": {
        "API_BASE_URL": "https://devshort.com",
        "DATABASE_URL": "sqlite+aiosqlite:///default.db",
        "ALEMBIC_DATABASE_URL": "",
        "JWT_AUTH_SECRET_KEY": "[DevShort]->S3cr3tK3y!@#$%&*()-+",
        "SENDGRID_API_KEY": "fake-sendgrid-key",
        "SENDGRID_FROM_EMAIL": "admin@gmail.com"
    },
    "testing": {
        "API_BASE_URL": "https://testshort.com",
        "DATABASE_URL": "sqlite+aiosqlite:///:memory:",
        "ALEMBIC_DATABASE_URL": "",
        "JWT_AUTH_SECRET_KEY": "[TestShort]->S3cr3tK3y!@#$%&*()-+",
        "SENDGRID_API_KEY": "fake-sendgrid-key",
        "SENDGRID_FROM_EMAIL": "admin@gmail.com"
    }
}
