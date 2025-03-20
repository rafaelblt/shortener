import pytest

from shortener.domain.shorturl.exceptions import (
    ShortURLSlugTooLongError,
    ShortURLSlugTooShortError,
    ShortURLInvalidSlugError,
    ShortURLForbiddenSlugError
)
from shortener.domain.shorturl.slug import (
    Slug,
    SLUG_MAX_LENGTH,
    SLUG_MIN_LENGTH
)


def test_method_validate_slug():
    assert Slug._validate_slug("test-valid") == None


def test_method_validate_slug_raises_slug_too_long():
    value = "a" * (SLUG_MAX_LENGTH + 1)
    with pytest.raises(
        ShortURLSlugTooLongError, 
        match=f"Slug must be at most {SLUG_MAX_LENGTH} characters long."
    ):
        Slug._validate_slug(value)


def test_method_validate_slug_raises_slug_too_short():
    value = "a" * (SLUG_MIN_LENGTH - 1)
    with pytest.raises(
        ShortURLSlugTooShortError, 
        match=f"Slug must be at least {SLUG_MIN_LENGTH} characters long."
    ):
        Slug._validate_slug(value)


def test_method_validate_slug_raises_forbidden_slug():
    value = "docs"
    with pytest.raises(
        ShortURLForbiddenSlugError,
        match="The provided slug is forbidden."
    ):
        Slug._validate_slug(value)


def test_method_validate_slug_raises_invalid_slug():
    value = "test.invalid"
    with pytest.raises(
        ShortURLInvalidSlugError,
        match="Slug contains invalid characters. Allowed: a-z, A-Z, 0-9, _, -"
    ):
        Slug._validate_slug(value)
