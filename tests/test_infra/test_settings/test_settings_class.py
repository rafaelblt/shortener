import pytest

from shortener.infra.settings import settings_class, loader


@pytest.fixture
def settings_dict():
    return loader.load_settings()


def test_instance():
    settings = settings_class.settings
    assert isinstance(settings, settings_class.Settings)


def test_attributes(settings_dict: dict[str, str]):
    settings = settings_class.settings
    assert settings.APP_NAME == settings_dict["APP_NAME"]
    assert settings.APP_VERSION == settings_dict["APP_VERSION"]
    assert settings.API_BASE_URL == settings_dict["API_BASE_URL"]
    assert settings.DATABASE_URL == settings_dict["DATABASE_URL"]
    assert settings.ALEMBIC_DATABASE_URL == settings_dict["ALEMBIC_DATABASE_URL"]
    assert settings.JWT_AUTH_SECRET_KEY == settings_dict["JWT_AUTH_SECRET_KEY"]
    assert settings.JWT_AUTH_TOKEN_ALGORITHM == settings_dict["JWT_AUTH_TOKEN_ALGORITHM"]
    assert settings.JWT_AUTH_TOKEN_EXPIRES_MINUTES == settings_dict["JWT_AUTH_TOKEN_EXPIRES_MINUTES"]
    assert settings.SENDGRID_API_KEY == settings_dict["SENDGRID_API_KEY"]
    assert settings.SENDGRID_FROM_EMAIL == settings_dict["SENDGRID_FROM_EMAIL"]
    assert settings.SUPPORTED_LANGUAGES == settings_dict["SUPPORTED_LANGUAGES"]

