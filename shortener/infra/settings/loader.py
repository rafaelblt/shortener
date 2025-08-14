import os

from typing import Any
from dotenv import load_dotenv

from shortener.infra.settings import constants
from shortener.infra.settings import utils
from shortener.infra import exceptions
from shortener.infra.settings.converters import ConversionError


load_dotenv()


def load_settings():
    settings: dict[str, Any] = {}

    set_default_settings(settings)
    get_and_set_env_template(settings)
    set_env_vars(settings)
    set_static_settings(settings)

    utils.validate_settings(settings)

    return settings


def set_default_settings(settings: dict):
    for item in [item for item in constants.ENV_VARS if item["default"]]:
        settings[item["settings_var"]] = item["default"]


def get_and_set_env_template(settings: dict):
    env_template = os.getenv("ENVIRONMENT_TEMPLATE")
    if not env_template:
        return
    if env_template not in constants.ENV_TEMPLATES:
        raise exceptions.UnknownEnvironmentTemplateError(
            unknown_template=env_template,
            available_templates=list(constants.ENV_TEMPLATES.keys())
        )
    settings.update(constants.ENV_TEMPLATES[env_template])


def set_env_vars(settings: dict):
    for item in constants.ENV_VARS:
        value = os.getenv(item["env_var"])
        if value is None:
            continue
        if item["converter"]:
            try:
                value = item["converter"](value)
            except ConversionError as e:
               raise exceptions.EnvironmentVariableConversionError(
                   var=item["env_var"], detail=str(e)
               )
        settings[item["settings_var"]] = value


def set_static_settings(settings: dict):
    settings.update(constants.STATIC_SETTINGS)
