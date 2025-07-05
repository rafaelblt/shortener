import os

from typing import TypedDict

from shortener.domain.shared.email import Email
from shortener.domain.shared.language import Language

from shortener.infra.exceptions import MissingEnvironmentVariableError


class StaticSettingsType(TypedDict):
    SUPPORTED_LANGUAGES: list[Language]


class EnvDefaultsType(TypedDict):
    APP_NAME: str
    JWT_AUTH_TOKEN_ALGORITHM: str
    JWT_AUTH_TOKEN_EXPIRES_MINUTES: str


class Settings:
    _STATIC_SETTINGS: StaticSettingsType = {
        "SUPPORTED_LANGUAGES": [Language.EN, Language.PT_BR]
    }

    _ENV_DEFAULTS: EnvDefaultsType = {
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
        self._env_vars = {}
        missing_vars = []

        for var, value in self._ENV_DEFAULTS.items():
            self._env_vars[var] = value

        for var in self._REQUIRED_ENV_VARS:
            value = os.getenv(var)
            if value is None:
                missing_vars.append(var)
            else:
                self._env_vars[var] = value
        
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
