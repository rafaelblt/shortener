import pytest

from shortener.domain.shared.parsing import require_non_empty_string
from tests.utils.text_helpers import assert_mentions


TYPE_NAME = "Slug"


def test_returns_a_non_empty_string():
    assert require_non_empty_string("abc", TYPE_NAME) == "abc"


@pytest.mark.parametrize("value", [123, None, b"abc"])
def test_rejects_a_value_that_is_not_a_string_with_type_error(value):
    with pytest.raises(TypeError) as raised:
        require_non_empty_string(value, TYPE_NAME)
    assert_mentions(str(raised.value), TYPE_NAME, str.__name__, type(value).__name__)


def test_rejects_an_empty_string_with_value_error():
    with pytest.raises(ValueError) as raised:
        require_non_empty_string("", TYPE_NAME)
    assert_mentions(str(raised.value), TYPE_NAME)
