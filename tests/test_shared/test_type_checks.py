import pytest

from shortener.shared.type_checks import check_parameter_type


def test_accepts_an_instance_of_the_expected_type():
    check_parameter_type("count", 1, int)


def test_accepts_an_instance_of_a_subclass_of_the_expected_type():
    check_parameter_type("count", True, int)


@pytest.mark.parametrize("value", ["1", 1.0, None])
def test_rejects_a_value_of_another_type_with_type_error(value):
    with pytest.raises(TypeError, match="The count parameter must be an instance of int"):
        check_parameter_type("count", value, int)


def test_type_error_names_the_type_received():
    with pytest.raises(TypeError, match="got str$"):
        check_parameter_type("count", "1", int)
