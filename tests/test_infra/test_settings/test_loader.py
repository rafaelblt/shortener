import os
import pytest

from unittest.mock import patch

from shortener.infra import exceptions
from shortener.infra.settings import constants, loader, converters


valid_values_conversion: dict[converters.ConverterFunc, str] = {
    converters.convert_str_minutes_to_timedelta: "10",
    converters.convert_str_to_email: "example@gmail.com"
}


def test_func_set_default_settings():
    settings = {"bla": "bla", "test": "abc"}

    expected_settings = settings.copy()
    for item in constants.ENV_VARS:
        if item["default"]:
            expected_settings[item["settings_var"]] = item["default"]

    loader.set_default_settings(settings)

    assert settings == expected_settings


def test_func_get_and_set_env_template():
    settings = {"bla": "bla", "test": "abc"}
    env_template = "development"

    expected_settings = settings.copy()
    expected_settings.update(constants.ENV_TEMPLATES[env_template])

    with patch.dict(os.environ):
        os.environ["ENVIRONMENT_TEMPLATE"] = env_template
        loader.get_and_set_env_template(settings)

    assert settings == expected_settings


def test_func_get_and_set_env_template_raises_unknown_template():
    settings = {}
    env_template = "UNKNOWN"
    available_templates = list(constants.ENV_TEMPLATES.keys())

    with patch.dict(os.environ):
        os.environ["ENVIRONMENT_TEMPLATE"] = env_template
        with pytest.raises(exceptions.UnknownEnvironmentTemplateError) as error:
            loader.get_and_set_env_template(settings)

    assert error.value.unknown_template == env_template
    assert error.value.available_templates == available_templates


def test_func_set_env_vars():
    settings = {}
    expected_settings = {}
    
    with patch.dict(os.environ):
        for i, item in enumerate(constants.ENV_VARS):
            if item["converter"]:
                value = valid_values_conversion[item["converter"]]
                expected_value = item["converter"](value)
            else:
                value = f"var_{i}"
                expected_value = value
            os.environ[item["env_var"]] = value
            expected_settings[item["settings_var"]] = expected_value
        loader.set_env_vars(settings)

    assert settings == expected_settings


def test_func_set_env_vars_raises_env_var_conversion_error():
    settings = {}
    expected_var = None
    expected_detail = None
    with patch.dict(os.environ):
        for item in constants.ENV_VARS:
            if item["converter"]:
                value = "<@O1Ij7364s7a457oid87f65j8aÇ8AQ9P0E5k3asD5P2O4p6x6zkpjmdsa)p(c-=DZA/,CsiodamCÁS-OD0FK#)J"
                os.environ[item["env_var"]] = value
                try:
                    item["converter"](value)
                except converters.ConversionError as e:
                    expected_var = item["env_var"]
                    expected_detail = str(e)
                    break
        with pytest.raises(exceptions.EnvironmentVariableConversionError) as e:
            loader.set_env_vars(settings)
        assert e.value.var == expected_var
        assert e.value.detail == expected_detail


def test_func_set_static_settings():
    settings = {"bla": "bla", "test": "abc"}

    expected_settings = settings.copy()
    expected_settings.update(constants.STATIC_SETTINGS)

    loader.set_static_settings(settings)

    assert settings == expected_settings


def test_func_load_settings_without_env_template():
    expected_settings = {}
    expected_settings.update(constants.STATIC_SETTINGS)

    with patch.dict(os.environ):
        for i, item in enumerate(constants.ENV_VARS):
            if item["converter"]:
                value = valid_values_conversion[item["converter"]]
                expected_value = item["converter"](value)
            else:
                value = f"var_{i}"
                expected_value = value
            os.environ[item["env_var"]] = value
            expected_settings[item["settings_var"]] = expected_value
        retrieved = loader.load_settings()

    assert retrieved == expected_settings


def test_func_load_settings_with_env_template():
    env_template = "testing"

    expected_settings = {}
    expected_settings.update(constants.STATIC_SETTINGS)
    expected_settings.update(constants.SETTINGS_DEFAULTS)
    expected_settings.update(constants.ENV_TEMPLATES[env_template])

    with patch.dict(os.environ):
        os.environ["ENVIRONMENT_TEMPLATE"] = env_template
        retrieved = loader.load_settings()

    assert retrieved == expected_settings


def test_func_load_settings_calls_validate_settings():
    with patch.dict(os.environ, clear=True):
        with pytest.raises(exceptions.MissingEnvironmentVariableError):
            loader.load_settings()
