import os
import tomllib

from typing import Any, List, Optional
from dataclasses import dataclass, field, fields
from datetime import timedelta
from dotenv import load_dotenv

from shortener.domain.shared.email import Email
from shortener.domain.shared.language import Language

from shortener.infra import exceptions

from . import converters


load_dotenv()


def get_project_app_version() -> str:
    with open("pyproject.toml", "rb") as f:
        data = tomllib.load(f)
    return data["project"]["version"]


def optional_env_var(var_name: str, default: Any, converter: Optional[converters.ConverterFunc] = None):
    def default_factory():
        value = os.getenv(var_name)
        if value is None:
            return default
        if converter:
            try:
                value = converter(value)
            except converters.ConversionError as e:
               raise exceptions.EnvironmentVariableConversionError(
                   var=var_name, detail=str(e)
               )
        return value
    return {"default_factory": default_factory, "metadata": {"is_required": False}}


def required_env_var(var_name: str, converter: Optional[converters.ConverterFunc] = None):
    def default_factory():
        value = os.getenv(var_name)
        if value is None:
            return None
        if converter:
            try:
                value = converter(value)
            except converters.ConversionError as e:
               raise exceptions.EnvironmentVariableConversionError(
                   var=var_name, detail=str(e)
               )
        return value
    return {"default_factory": default_factory, "metadata": {"is_required": True}}


def static_var(value: Any):
    def default_factory():
        return value
    return {"default_factory": default_factory, "metadata": {"is_required": False}}


@dataclass(frozen=True)
class Settings:
    app_name: str = field(**optional_env_var(var_name="APP_NAME", default="Shortener"))
    app_version: str = field(**static_var(value=get_project_app_version()))

    api_base_url: str = field(**required_env_var(var_name="API_BASE_URL"))
    database_url: str = field(**required_env_var(var_name="DATABASE_URL"))
    alembic_database_url: str = field(**required_env_var(var_name="ALEMBIC_DATABASE_URL"))

    jwt_secret_key: str = field(**required_env_var(var_name="JWT_SECRET_KEY"))
    jwt_algorithm: str = field(**optional_env_var(var_name="JWT_ALGORITHM", default="HS256"))

    sendgrid_api_key: str = field(**required_env_var(var_name="SENDGRID_API_KEY"))
    sendgrid_from_email: Email = field(**required_env_var(var_name="SENDGRID_FROM_EMAIL"))

    access_token_expiration: timedelta = field(**optional_env_var(
        var_name="ACCESS_TOKEN_EXPIRATION_MINUTES",
        default=timedelta(minutes=15),
        converter=converters.str_minutes_to_timedelta
    ))
    refresh_token_expiration: timedelta = field(**optional_env_var(
        var_name="REFRESH_TOKEN_EXPIRATION_MINUTES",
        default=timedelta(minutes=60),
        converter=converters.str_minutes_to_timedelta
    ))
    email_verification_expiration: timedelta = field(**optional_env_var(
        var_name="EMAIL_VERIFICATION_EXPIRATION_MINUTES",
        default=timedelta(minutes=30),
        converter=converters.str_minutes_to_timedelta
    ))
    
    supported_languages: List[Language] = field(**static_var([Language.EN, Language.PT_BR]))

    plan_repository_impl: str = field(**optional_env_var(
        var_name="PLAN_REPOSITORY_IMPL", default="sqlalchemy"
    ))
    user_repository_impl: str = field(**optional_env_var(
        var_name="USER_REPOSITORY_IMPL", default="sqlalchemy"
    ))
    shorturl_repository_impl: str = field(**optional_env_var(
        var_name="SHORTURL_REPOSITORY_IMPL", default="sqlalchemy"
    ))

    access_token_service_impl: str = field(**optional_env_var(
        var_name="ACCESS_TOKEN_SERVICE_IMPL", default="jwt"
    ))
    refresh_token_service_impl: str = field(**optional_env_var(
        var_name="REFRESH_TOKEN_SERVICE_IMPL", default="jwt"
    ))
    verify_email_token_service_impl: str = field(**optional_env_var(
        var_name="VERIFY_EMAIL_TOKEN_SERVICE_IMPL", default="jwt"
    ))
    password_hasher_service_impl: str = field(**optional_env_var(
        var_name="PASSWORD_HASHER_SERVICE_IMPL", default="passlib"
    ))
    send_email_service_impl: str = field(**optional_env_var(
        var_name="SEND_EMAIL_SERVICE_IMPL", default="sendgrid"
    ))

    @classmethod
    def load(cls) -> "Settings":
        settings = Settings() # type: ignore
        settings.validate_missing_required_vars()
        return settings

    def validate_missing_required_vars(self):
        missing_required_vars = []
        for field in fields(Settings):
            value = self.__getattribute__(field.name)
            if value is None:
                if not field.metadata["is_required"]:
                    raise ValueError(
                        (f"The settings variable '{field.name}' is defined as not "
                        "required but retrieve None instead of a valid default value.")
                    )
                else:
                    missing_required_vars.append(field.name)
        if missing_required_vars:
            raise exceptions.MissingEnvironmentVariableError(missing_required_vars)


def get_settings():
    return Settings.load()


settings = Settings.load()
