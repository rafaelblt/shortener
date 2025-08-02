import tomllib

from shortener.infra.exceptions import MissingEnvironmentVariableError
from shortener.infra.settings import constants


def get_project_app_version():
    with open("pyproject.toml", "rb") as f:
        data = tomllib.load(f)
    return data["project"]["version"]


def validate_settings(settings: dict[str, str]):
    missing_vars = []
    for item in constants.REQUIRED_ENV_VARS:
        if item["settings_var"] not in settings:
            missing_vars.append(item["env_var"])
    if missing_vars:
        raise MissingEnvironmentVariableError(missing_vars)
