import pytest

from shortener.domain.shorturl.fields.slug import Slug, SLUG_MAX_LENGTH


def test_returns_a_slug_with_the_value():
    slug = Slug.parse("my-slug")
    assert isinstance(slug, Slug)
    assert slug == "my-slug"


@pytest.mark.parametrize(
    "value", ["docs", "a", "a" * (SLUG_MAX_LENGTH + 1), "dot.slug"]
)
def test_accepts_a_value_that_breaks_the_rules_of_create(value):
    assert Slug.parse(value) == value


@pytest.mark.parametrize("value", [12345, None])
def test_rejects_a_value_that_is_not_a_string_with_type_error(value):
    with pytest.raises(TypeError, match="Slug must be a str"):
        Slug.parse(value)


def test_rejects_an_empty_string_with_value_error():
    with pytest.raises(ValueError, match="Slug must not be empty"):
        Slug.parse("")
