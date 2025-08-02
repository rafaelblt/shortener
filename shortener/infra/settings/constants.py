from datetime import timedelta
from typing import Any, Optional, TypedDict

from shortener.domain.shared.email import Email
from shortener.domain.shared.language import Language

from .utils import get_project_app_version
from .converters import ConverterFunc, convert_str_minutes_to_timedelta, convert_str_to_email


class EnvVarType(TypedDict):
    env_var: str
    settings_var: str
    is_required: bool
    default: Optional[Any]
    converter: Optional[ConverterFunc]


STATIC_SETTINGS = {
    "APP_VERSION": get_project_app_version(),
    "SUPPORTED_LANGUAGES": [Language.EN, Language.PT_BR]
}


ENV_VARS = [
    EnvVarType(
        env_var="API_BASE_URL",
        settings_var="API_BASE_URL",
        is_required=True,
        default=None,
        converter=None
    ),
    EnvVarType(
        env_var="DATABASE_URL",
        settings_var="DATABASE_URL",
        is_required=True,
        default=None,
        converter=None
    ),
    EnvVarType(
        env_var="ALEMBIC_DATABASE_URL",
        settings_var="ALEMBIC_DATABASE_URL",
        is_required=True,
        default=None,
        converter=None
    ),
    EnvVarType(
        env_var="JWT_SECRET_KEY",
        settings_var="JWT_SECRET_KEY",
        is_required=True,
        default=None,
        converter=None
    ),
    EnvVarType(
        env_var="SENDGRID_API_KEY",
        settings_var="SENDGRID_API_KEY",
        is_required=True,
        default=None,
        converter=None
    ),

    EnvVarType(
        env_var="SENDGRID_FROM_EMAIL",
        settings_var="SENDGRID_FROM_EMAIL",
        is_required=True,
        default=None,
        converter=convert_str_to_email
    ),

    EnvVarType(
        env_var="APP_NAME",
        settings_var="APP_NAME",
        is_required=False,
        default="Shortener",
        converter=None
    ),
    EnvVarType(
        env_var="JWT_ALGORITHM",
        settings_var="JWT_ALGORITHM",
        is_required=False,
        default="HS256",
        converter=None
    ),
    EnvVarType(
        env_var="ACCESS_TOKEN_EXPIRATION_MINUTES",
        settings_var="ACCESS_TOKEN_EXPIRATION",
        is_required=False,
        default=timedelta(minutes=15),
        converter=convert_str_minutes_to_timedelta
    ),
    EnvVarType(
        env_var="REFRESH_TOKEN_EXPIRATION_MINUTES",
        settings_var="REFRESH_TOKEN_EXPIRATION",
        is_required=False,
        default=timedelta(minutes=60),
        converter=convert_str_minutes_to_timedelta
    ),
    EnvVarType(
        env_var="EMAIL_VERIFICATION_EXPIRATION_MINUTES",
        settings_var="EMAIL_VERIFICATION_EXPIRATION",
        is_required=False,
        default=timedelta(minutes=30),
        converter=convert_str_minutes_to_timedelta
    ),
]


REQUIRED_ENV_VARS = [var for var in ENV_VARS if var["is_required"]]
SETTINGS_DEFAULTS = {var["settings_var"]: var["default"] for var in ENV_VARS if var["default"]}


ENV_TEMPLATES: dict[str, dict[str, str]] = {
    "development": {
        "API_BASE_URL": "https://devshort.com",
        "DATABASE_URL": "sqlite+aiosqlite:///default.db",
        "ALEMBIC_DATABASE_URL": "sqlite:///default.db",
        "JWT_SECRET_KEY": "[DevShort]->S3cr3tK3y!@#$%&*()-+",
        "SENDGRID_API_KEY": "fake-sendgrid-key",
        "SENDGRID_FROM_EMAIL": Email("admin@gmail.com")
    },
    "testing": {
        "API_BASE_URL": "https://testshort.com",
        "DATABASE_URL": "sqlite+aiosqlite:///:memory:",
        "ALEMBIC_DATABASE_URL": "",
        "JWT_SECRET_KEY": "[TestShort]->S3cr3tK3y!@#$%&*()-+",
        "SENDGRID_API_KEY": "fake-sendgrid-key",
        "SENDGRID_FROM_EMAIL": Email("admin@gmail.com")
    }
}
