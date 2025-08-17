import pytest

from shortener.domain.shorturl.exceptions import (
    ShortURLSlugTooLongError,
    ShortURLSlugTooShortError,
    ShortURLInvalidSlugError,
    ShortURLForbiddenSlugError
)
from shortener.domain.shorturl.fields.slug import (
    Slug,
    SLUG_MAX_LENGTH,
    SLUG_MIN_LENGTH
)


def test_validate_slug():
    assert Slug.validate_slug("test-valid") == None


def test_validate_slug_raises_slug_too_long():
    value = "a" * (SLUG_MAX_LENGTH + 1)
    with pytest.raises(ShortURLSlugTooLongError) as error:
        Slug.validate_slug(value)
    assert error.value.slug == value
    assert error.value.max_length == SLUG_MAX_LENGTH


def test_validate_slug_raises_slug_too_short():
    value = "a" * (SLUG_MIN_LENGTH - 1)
    with pytest.raises(ShortURLSlugTooShortError) as error:
        Slug.validate_slug(value)
    assert error.value.slug == value
    assert error.value.min_length == SLUG_MIN_LENGTH


def test_validate_slug_raises_forbidden_slug():
    value = "docs"
    with pytest.raises(ShortURLForbiddenSlugError) as error:
        Slug.validate_slug(value)
    assert error.value.slug == value


def test_validate_slug_raises_invalid_slug():
    value = "test.invalid"
    with pytest.raises(ShortURLInvalidSlugError) as error:
        Slug.validate_slug(value)
    assert error.value.slug == value
