import os
import pytest

from unittest.mock import patch

from shortener.infra.exceptions import MissingEnvironmentVariableError
from shortener.infra.settings import constants, loader


def test_func_set_default_env_vars():
    settings = {"bla": "bla", "test": "abc"}

    expected_settings = settings.copy()
    expected_settings.update(constants.ENV_DEFAULTS)

    loader.set_default_env_vars(settings)

    assert settings == expected_settings


def test_func_get_and_set_env_pattern():
    settings = {"bla": "bla", "test": "abc"}
    env_pattern = "development"

    expected_settings = settings.copy()
    expected_settings.update(constants.ENV_PATTERNS[env_pattern])

    os.environ["ENVIRONMENT_PATTERN"] = env_pattern
    loader.get_and_set_env_pattern(settings)

    assert settings == expected_settings


def test_func_set_required_env_vars():
    settings = {"bla": "bla", "test": "abc"}
    expected_settings = settings.copy()

    for i, var in enumerate(constants.REQUIRED_ENV_VARS):
        value = f"var{i}"
        os.environ[var] = value 
        expected_settings[var] = value

    loader.set_required_env_vars(settings)

    assert settings == expected_settings


def test_func_set_optional_env_vars():
    settings = {"bla": "bla", "test": "abc"}
    expected_settings = settings.copy()

    for i, var in enumerate(constants.OPTIONAL_ENV_VARS):
        value = f"var{i}"
        os.environ[var] = value 
        expected_settings[var] = value

    loader.set_optional_env_vars(settings)

    assert settings == expected_settings


def test_func_set_static_settings():
    settings = {"bla": "bla", "test": "abc"}

    expected_settings = settings.copy()
    expected_settings.update(constants.STATIC_SETTINGS)

    loader.set_static_settings(settings)

    assert settings == expected_settings


def test_func_load_settings_without_env_pattern():
    expected_settings = {}

    for i, var in enumerate(constants.REQUIRED_ENV_VARS):
        value = f"required_{i}"
        os.environ[var] = value
        expected_settings[var] = value
    
    expected_settings.update(constants.STATIC_SETTINGS)
    expected_settings.update(constants.ENV_DEFAULTS)

    retrieved = loader.load_settings()

    assert retrieved == expected_settings


def test_func_load_settings_with_env_pattern():
    env_pattern = "testing"

    expected_settings = {}
    expected_settings.update(constants.STATIC_SETTINGS)
    expected_settings.update(constants.ENV_DEFAULTS)
    expected_settings.update(constants.ENV_PATTERNS[env_pattern])

    os.environ["ENVIRONMENT_PATTERN"] = env_pattern

    retrieved = loader.load_settings()

    assert retrieved == expected_settings


def test_func_load_settings_calls_validate_settings():
    with patch.dict(os.environ, clear=True):
        with pytest.raises(MissingEnvironmentVariableError):
            loader.load_settings()
