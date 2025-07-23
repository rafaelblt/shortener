import pytest

from shortener.infra.settings import constants
from shortener.infra.settings.utils import validate_settings
from shortener.infra.exceptions import MissingEnvironmentVariableError


def test_func_validate_settings():
    settings = {var: var for var in constants.REQUIRED_ENV_VARS}
    validate_settings(settings)


def test_func_validate_settings_raises_error():
    settings = {}
    missing_vars = constants.REQUIRED_ENV_VARS
    with pytest.raises(MissingEnvironmentVariableError) as error:
        validate_settings(settings)
    assert error.value.var_names == missing_vars
