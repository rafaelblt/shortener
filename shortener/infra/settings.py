import os

from dotenv import load_dotenv
from typing import TypedDict

from shortener.domain.shared.email import Email
from shortener.domain.shared.language import Language

from shortener.infra.exceptions import MissingEnvironmentVariableError


load_dotenv()


ENV_PATTERNS: dict[str, dict] = {
    "development": {
        "API_BASE_URL": "https://devshort.com",
        "DATABASE_URL": "sqlite+aiosqlite:///default.db",
        "ALEMBIC_DATABASE_URL": "",
        "JWT_AUTH_SECRET_KEY": "[DevShort]->S3cr3tK3y!@#$%&*()-+",
        "SENDGRID_API_KEY": "fake-sendgrid-key",
        "SENDGRID_FROM_EMAIL": "admin@gmail.com"
    }
}


class StaticSettingsType(TypedDict):
    SUPPORTED_LANGUAGES: list[Language]


class Settings:
    _STATIC_SETTINGS: StaticSettingsType = {
        "SUPPORTED_LANGUAGES": [Language.EN, Language.PT_BR]
    }

    _ENV_DEFAULTS: dict[str, str] = {
        "APP_NAME": "Shortener",
        "JWT_AUTH_TOKEN_ALGORITHM": "HS256",
        "JWT_AUTH_TOKEN_EXPIRES_MINUTES": "60",
    }

    _REQUIRED_ENV_VARS = [
        "API_BASE_URL",
        "DATABASE_URL",
        "ALEMBIC_DATABASE_URL",
        "JWT_AUTH_SECRET_KEY",
        "SENDGRID_API_KEY",
        "SENDGRID_FROM_EMAIL"
    ]

    def __init__(self):
        self._env_vars: dict[str, str] = {}

        self._set_default_env_vars()
        self._get_and_set_env_pattern()
        self._set_required_env_vars()
        self._verify_required_env_vars()
    
    def _set_default_env_vars(self):
        for var, value in self._ENV_DEFAULTS.items():
            self._env_vars[var] = value

    def _get_and_set_env_pattern(self):
        env_pattern = os.getenv("ENVIRONMENT_PATTERN")
        if env_pattern and env_pattern in ENV_PATTERNS:
            self._env_vars.update(ENV_PATTERNS[env_pattern])
    
    def _set_required_env_vars(self):
        for var in self._REQUIRED_ENV_VARS:
            value = os.getenv(var)
            if value is not None:
                self._env_vars[var] = value

    def _verify_required_env_vars(self):
        missing_vars = []

        for var in self._REQUIRED_ENV_VARS:
            if var not in self._env_vars:
                missing_vars.append(var)

        if missing_vars:
            raise MissingEnvironmentVariableError(missing_vars)

    @property
    def APP_NAME(self):
        return self._env_vars["APP_NAME"]

    @property
    def API_BASE_URL(self):
        return self._env_vars["API_BASE_URL"]

    @property
    def DATABASE_URL(self):
        return self._env_vars["DATABASE_URL"]

    @property
    def ALEMBIC_DATABASE_URL(self):
        return self._env_vars["ALEMBIC_DATABASE_URL"]

    @property
    def JWT_AUTH_SECRET_KEY(self):
        return self._env_vars["JWT_AUTH_SECRET_KEY"]

    @property
    def JWT_AUTH_TOKEN_ALGORITHM(self):
        return self._env_vars["JWT_AUTH_TOKEN_ALGORITHM"]

    @property
    def JWT_AUTH_TOKEN_EXPIRES_MINUTES(self):
        value = self._env_vars["JWT_AUTH_TOKEN_EXPIRES_MINUTES"]
        return int(value)

    @property
    def SENDGRID_API_KEY(self):
        return self._env_vars["SENDGRID_API_KEY"]

    @property
    def SENDGRID_FROM_EMAIL(self):
        value = self._env_vars["SENDGRID_FROM_EMAIL"]
        return Email(value)
    
    @property
    def SUPPORTED_LANGUAGES(self):
        return self._STATIC_SETTINGS["SUPPORTED_LANGUAGES"]


settings = Settings()
