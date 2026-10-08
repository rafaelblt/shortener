import pytest

from shortener.domain.shorturl.slug import Slug, SLUG_MAX_LENGTH
from tests.utils.text_helpers import assert_mentions


def test_returns_a_slug_with_the_value():
    slug = Slug.parse("my-slug")
    assert isinstance(slug, Slug)
    assert slug == "my-slug"


@pytest.mark.parametrize(
    "value", ["a", "a" * (SLUG_MAX_LENGTH + 1), "dot.slug"]
)
def test_accepts_a_value_that_breaks_the_rules_of_create(value):
    assert Slug.parse(value) == value


@pytest.mark.parametrize("value", [12345, None])
def test_rejects_a_value_that_is_not_a_string_with_type_error(value):
    with pytest.raises(TypeError) as raised:
        Slug.parse(value)
    assert_mentions(str(raised.value), Slug.__name__)


def test_rejects_an_empty_string_with_value_error():
    with pytest.raises(ValueError) as raised:
        Slug.parse("")
    assert_mentions(str(raised.value), Slug.__name__)
