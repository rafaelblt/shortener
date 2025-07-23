import tomllib

from shortener.infra.exceptions import MissingEnvironmentVariableError
from shortener.infra.settings import constants


def get_project_app_version():
    with open("pyproject.toml", "rb") as f:
        data = tomllib.load(f)
    return data["project"]["version"]


def validate_settings(settings: dict[str, str]):
    missing_vars = []
    for var in constants.REQUIRED_ENV_VARS:
        if var not in settings:
            missing_vars.append(var)
    if missing_vars:
        raise MissingEnvironmentVariableError(missing_vars)
