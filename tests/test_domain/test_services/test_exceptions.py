import pytest
import re

from shortener.domain.services.exceptions import *


def test_missing_template_variable():
    var_names = ["a", "b", "c"]
    text = re.escape(f"Missing required template variables: {var_names}")
    with pytest.raises(MissingTemplateVariableError, match=text) as error:
        raise MissingTemplateVariableError(var_names)
    assert error.value.var_names == var_names
