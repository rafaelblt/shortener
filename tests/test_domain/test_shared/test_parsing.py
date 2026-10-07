import pytest

from shortener.domain.shared.parsing import require_non_empty_string


def test_returns_a_non_empty_string():
    assert require_non_empty_string("abc", "Slug") == "abc"


@pytest.mark.parametrize("value", [123, None, b"abc"])
def test_rejects_a_value_that_is_not_a_string_with_type_error(value):
    with pytest.raises(TypeError, match="Slug must be a str, got"):
        require_non_empty_string(value, "Slug")


def test_rejects_an_empty_string_with_value_error():
    with pytest.raises(ValueError, match="Slug must not be empty"):
        require_non_empty_string("", "Slug")
