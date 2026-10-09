import pytest

from shortener.shared.type_checks import check_parameter_type
from tests.utils.text_helpers import assert_mentions


PARAMETER = "count"


def test_accepts_an_instance_of_the_expected_type():
    check_parameter_type(PARAMETER, 1, int)


def test_accepts_an_instance_of_a_subclass_of_the_expected_type():
    check_parameter_type(PARAMETER, True, int)


@pytest.mark.parametrize("value", ["1", 1.0, None])
def test_rejects_a_value_of_another_type_with_type_error(value: object):
    with pytest.raises(TypeError) as raised:
        check_parameter_type(PARAMETER, value, int)
    assert_mentions(str(raised.value), PARAMETER, int.__name__, type(value).__name__)
