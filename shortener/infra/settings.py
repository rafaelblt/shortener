import os

from shortener.domain.shared.email import Email
from shortener.infra.exceptions import MissingEnvironmentVariableError


class Settings:
    def __init__(self):
        self._database_url = self.get_database_url()
        self._alembic_database_url = self.get_alembic_database_url()
        self._jwt_auth_secret_key = self.get_jwt_auth_secret_key()
        self._jwt_auth_token_algorithm = self.get_jwt_auth_token_algorithm()
        self._jwt_auth_token_expires_minutes = self.get_jwt_auth_token_expires_minutes()
        self._sendgrid_api_key = self.get_sendgrid_api_key()
        self._sendgrid_from_email = self.get_sendgrid_from_email()

    @property
    def DATABASE_URL(self) -> str:
        return self._database_url

    @property
    def ALEMBIC_DATABASE_URL(self) -> str:
        return self._alembic_database_url

    @property
    def JWT_AUTH_SECRET_KEY(self) -> str:
        return self._jwt_auth_secret_key

    @property
    def JWT_AUTH_TOKEN_ALGORITHM(self) -> str:
        return self._jwt_auth_token_algorithm

    @property
    def JWT_AUTH_TOKEN_EXPIRES_MINUTES(self) -> int:
        return self._jwt_auth_token_expires_minutes

    @property
    def SENDGRID_API_KEY(self) -> str:
        return self._sendgrid_api_key

    @property
    def SENDGRID_FROM_EMAIL(self) -> Email:
        return self._sendgrid_from_email

    def get_database_url(self) -> str:
        return os.getenv("DATABASE_URL", "sqlite+aiosqlite:///default.db")

    def get_alembic_database_url(self) -> str:
        return os.getenv("ALEMBIC_DATABASE_URL", "sqlite:///default.db")

    def get_jwt_auth_secret_key(self) -> str:
        return os.getenv("JWT_AUTH_SECRET_KEY", "ko@34i!1@!3$!345Aba71")
    
    def get_jwt_auth_token_algorithm(self) -> str:
        return os.getenv("JWT_AUTH_TOKEN_ALGORITHM", "HS256")
    
    def get_jwt_auth_token_expires_minutes(self) -> int:
        return int(os.getenv("JWT_AUTH_TOKEN_EXPIRES_MINUTES", 60))
    
    def get_sendgrid_api_key(self) -> str:
        value = self.require_env("SENDGRID_API_KEY")
        return value
    
    def get_sendgrid_from_email(self) -> Email:
        value = self.require_env("SENDGRID_FROM_EMAIL")
        return Email(value)
    
    def require_env(self, key: str) -> str:
        value = os.getenv(key)
        if value is None:
            raise MissingEnvironmentVariableError(key)
        return value


settings = Settings()
