import os

from shortener.infra.settings import constants
from shortener.infra.settings import utils


def load_settings():
    settings: dict[str, str] = {}

    set_default_env_vars(settings)
    get_and_set_env_pattern(settings)
    set_required_env_vars(settings)
    set_optional_env_vars(settings)
    set_static_settings(settings)

    utils.validate_settings(settings)

    return settings


def set_default_env_vars(settings: dict):
    settings.update(constants.ENV_DEFAULTS)


def get_and_set_env_pattern(settings: dict):
    env_pattern = os.getenv("ENVIRONMENT_PATTERN")
    if env_pattern and env_pattern in constants.ENV_PATTERNS:
        settings.update(constants.ENV_PATTERNS[env_pattern])


def set_required_env_vars(settings: dict):
    for var in constants.REQUIRED_ENV_VARS:
        value = os.getenv(var)
        if value is not None:
            settings[var] = value


def set_optional_env_vars(settings: dict):
    for var in constants.OPTIONAL_ENV_VARS:
        value = os.getenv(var)
        if value is not None:
            settings[var] = value


def set_static_settings(settings: dict):
    settings.update(constants.STATIC_SETTINGS)
