import pytest
import re

from shortener.infra.exceptions import MissingEnvironmentVariableError


def test_missing_env_vars():
    var_names = ["t1", "t2", "t3", "t4"]
    err_msg = re.escape(f"Missing required environment variables: {var_names}")
    with pytest.raises(MissingEnvironmentVariableError, match=err_msg):
        raise MissingEnvironmentVariableError(var_names)
