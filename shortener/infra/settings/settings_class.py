from dataclasses import dataclass
from datetime import timedelta

from shortener.domain.shared.email import Email
from shortener.domain.shared.language import Language

from .loader import load_settings


settings_dict = load_settings()


@dataclass(frozen=True)
class Settings:
    APP_NAME: str = settings_dict["APP_NAME"]
    APP_VERSION: str = settings_dict["APP_VERSION"]

    API_BASE_URL: str = settings_dict["API_BASE_URL"]

    DATABASE_URL: str = settings_dict["DATABASE_URL"]
    ALEMBIC_DATABASE_URL: str = settings_dict["ALEMBIC_DATABASE_URL"]

    JWT_SECRET_KEY: str = settings_dict["JWT_SECRET_KEY"]
    JWT_ALGORITHM: str = settings_dict["JWT_ALGORITHM"]

    SENDGRID_API_KEY: str = settings_dict["SENDGRID_API_KEY"]
    SENDGRID_FROM_EMAIL: Email = settings_dict["SENDGRID_FROM_EMAIL"]

    ACCESS_TOKEN_EXPIRATION: timedelta = settings_dict["ACCESS_TOKEN_EXPIRATION"]
    REFRESH_TOKEN_EXPIRATION: timedelta = settings_dict["REFRESH_TOKEN_EXPIRATION"]
    EMAIL_VERIFICATION_EXPIRATION: timedelta = settings_dict["EMAIL_VERIFICATION_EXPIRATION"]
    
    SUPPORTED_LANGUAGES = settings_dict["SUPPORTED_LANGUAGES"]


settings = Settings()
