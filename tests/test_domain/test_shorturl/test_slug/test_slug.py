import pytest

from shortener.domain.shorturl.fields.slug import Slug
from shortener.domain.shorturl.exceptions import ShortURLInvalidSlugError


def test_new_slug():
    slug = Slug("test")
    assert isinstance(slug, Slug)
    assert isinstance(slug, str)
    assert slug == "test"


def test_new_slug_with_invalid_value():
    value = "test.invalid"
    with pytest.raises(ShortURLInvalidSlugError):
        Slug(value)
