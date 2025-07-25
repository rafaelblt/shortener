from dataclasses import dataclass
from .loader import load_settings


settings_dict = load_settings()


@dataclass(frozen=True)
class Settings:
    APP_NAME = settings_dict["APP_NAME"]
    APP_VERSION = settings_dict["APP_VERSION"]

    API_BASE_URL = settings_dict["API_BASE_URL"]

    DATABASE_URL = settings_dict["DATABASE_URL"]
    ALEMBIC_DATABASE_URL = settings_dict["ALEMBIC_DATABASE_URL"]

    JWT_SECRET_KEY = settings_dict["JWT_SECRET_KEY"]
    JWT_ALGORITHM = settings_dict["JWT_ALGORITHM"]

    SENDGRID_API_KEY = settings_dict["SENDGRID_API_KEY"]
    SENDGRID_FROM_EMAIL = settings_dict["SENDGRID_FROM_EMAIL"]

    EMAIL_VERIFICATION_EXPIRATION_MINUTES = settings_dict["EMAIL_VERIFICATION_EXPIRATION_MINUTES"]
    
    SUPPORTED_LANGUAGES = settings_dict["SUPPORTED_LANGUAGES"]


settings = Settings()
