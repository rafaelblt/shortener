import os
import pytest

from dataclasses import fields
from unittest.mock import patch

from shortener.infra.settings.settings_class import (
    get_project_app_version, get_settings, reload_settings, Settings
)
from shortener.infra.exceptions import MissingEnvironmentVariableError


def test_get_settings_instance():
    settings = get_settings()
    assert isinstance(settings, Settings)


def test_settings_instance():
    from shortener.infra.settings import settings
    assert isinstance(settings, Settings)


def test_attributes():
    with patch.dict(os.environ, clear=True):
        os.environ["APP_NAME"] = "test_app"
        os.environ["APP_VERSION"] = get_project_app_version()

        os.environ["API_BASE_URL"] = "https://testshort.com"
        os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
        os.environ["ALEMBIC_DATABASE_URL"] = "http://alembic_url"

        os.environ["JWT_SECRET_KEY"] = "[TestShort]->S3cr3tK3y!@#$%&*()-+"
        os.environ["JWT_ALGORITHM"] = "super_algo"

        os.environ["SENDGRID_API_KEY"] = "fake-sendgrid-key"
        os.environ["SENDGRID_FROM_EMAIL"] = "admin@gmail.com"

        os.environ["ACCESS_TOKEN_EXPIRATION_MINUTES"] = "10"
        os.environ["REFRESH_TOKEN_EXPIRATION_MINUTES"] = "20"
        os.environ["EMAIL_VERIFICATION_EXPIRATION_MINUTES"] = "30"

        os.environ["PLAN_REPOSITORY_IMPL"] = "test_PLAN_REPOSITORY_IMPL"
        os.environ["USER_REPOSITORY_IMPL"] = "test_USER_REPOSITORY_IMPL"
        os.environ["SHORTURL_REPOSITORY_IMPL"] = "test_SHORTURL_REPOSITORY_IMPL"
        os.environ["ACCESS_TOKEN_SERVICE_IMPL"] = "test_ACCESS_TOKEN_SERVICE_IMPL"
        os.environ["REFRESH_TOKEN_SERVICE_IMPL"] = "test_REFRESH_TOKEN_SERVICE_IMPL"
        os.environ["VERIFY_EMAIL_TOKEN_SERVICE_IMPL"] = "test_VERIFY_EMAIL_TOKEN_SERVICE_IMPL"
        os.environ["PASSWORD_HASHER_SERVICE_IMPL"] = "test_PASSWORD_HASHER_SERVICE_IMPL"
        os.environ["SEND_EMAIL_SERVICE_IMPL"] = "test_SEND_EMAIL_SERVICE_IMPL"

        reload_settings()
        settings = get_settings()

        assert settings.app_name == os.environ["APP_NAME"]
        assert settings.app_version == os.environ["APP_VERSION"]

        assert settings.api_base_url == os.environ["API_BASE_URL"]
        assert settings.database_url == os.environ["DATABASE_URL"]
        assert settings.alembic_database_url == os.environ["ALEMBIC_DATABASE_URL"]

        assert settings.jwt_secret_key == os.environ["JWT_SECRET_KEY"]
        assert settings.jwt_algorithm == os.environ["JWT_ALGORITHM"]

        assert settings.sendgrid_api_key == os.environ["SENDGRID_API_KEY"]
        assert str(settings.sendgrid_from_email) == os.environ["SENDGRID_FROM_EMAIL"]

        assert str(int(settings.access_token_expiration.seconds / 60)) == os.environ["ACCESS_TOKEN_EXPIRATION_MINUTES"]
        assert str(int(settings.refresh_token_expiration.seconds / 60)) == os.environ["REFRESH_TOKEN_EXPIRATION_MINUTES"]
        assert str(int(settings.email_verification_expiration.seconds / 60)) == os.environ["EMAIL_VERIFICATION_EXPIRATION_MINUTES"]

        assert settings.plan_repository_impl == os.environ["PLAN_REPOSITORY_IMPL"]
        assert settings.user_repository_impl == os.environ["USER_REPOSITORY_IMPL"]
        assert settings.shorturl_repository_impl == os.environ["SHORTURL_REPOSITORY_IMPL"]
        assert settings.access_token_service_impl == os.environ["ACCESS_TOKEN_SERVICE_IMPL"]
        assert settings.refresh_token_service_impl == os.environ["REFRESH_TOKEN_SERVICE_IMPL"]
        assert settings.verify_email_token_service_impl == os.environ["VERIFY_EMAIL_TOKEN_SERVICE_IMPL"]
        assert settings.password_hasher_service_impl == os.environ["PASSWORD_HASHER_SERVICE_IMPL"]
        assert settings.send_email_service_impl == os.environ["SEND_EMAIL_SERVICE_IMPL"]


def test_missing_required_env_vars():
    expected_missing_vars = []
    for field in fields(Settings):
        if field.metadata["is_required"]:
            expected_missing_vars.append(field.name)
    with patch.dict(os.environ, clear=True):
        with pytest.raises(MissingEnvironmentVariableError) as e:
            reload_settings()
    assert e.value.missing_vars == expected_missing_vars
