from pytest import fixture, raises

from shortener.domain.shorturl import ShortURL
from shortener.domain.shorturl.validators import GeneralValidator
from shortener.domain.shorturl.rules.slug_length import (
    SLUG_MAX_LENGTH, SLUG_MIN_LENGTH
)
from shortener.domain.shorturl.exceptions import (
    ShortURLForbiddenSlugError, 
    ShortURLSlugAlreadyExistsError,
    ShortURLSlugTooLongError,
    ShortURLSlugTooShortError
)


@fixture
def validator(mock_shorturl_repository):
    return GeneralValidator(repository=mock_shorturl_repository)


def test_validate_valid_slug(validator):
    assert validator._validate_slug("my-short-url") == None


def test_validate_forbidden_slug(validator):
    with raises(
        ShortURLForbiddenSlugError, match="The provided slug is forbidden."
    ):
        validator._validate_slug("api")


def test_validate_longer_slug(validator):
    slug = "a" * (SLUG_MAX_LENGTH + 1)

    with raises(
        ShortURLSlugTooLongError, 
        match="The provided slug is longer than max length"
    ):
        validator._validate_slug(slug)


def test_validate_slug_with_exactly_maxlength(validator):
    slug = "a" * SLUG_MAX_LENGTH 
    validator._validate_slug(slug)


def test_validate_shorter_slug(validator):
    slug = "a" * (SLUG_MIN_LENGTH - 1)

    with raises(
        ShortURLSlugTooShortError, 
        match="The provided slug is shorter than min length"
    ):
        validator._validate_slug(slug)


def test_validate_slug_with_exactly_min_length(validator):
    slug = "a" * SLUG_MIN_LENGTH
    validator._validate_slug(slug)


def test_validate_already_exists_slug(validator):
    validator.repository.save(ShortURL(slug="example", original_url="test.com"))

    with raises(
        ShortURLSlugAlreadyExistsError, match="The provided slug already exists."
    ):
        validator._validate_slug("example")


def test_validate_valid_shorturl(validator, normal_shorturl):
    assert validator.validate(normal_shorturl) == None


def test_validate_invalid_shorturl(validator):
    invalid_shorturl = ShortURL(slug="config", original_url="example.com")

    with raises(
        ShortURLForbiddenSlugError, match="The provided slug is forbidden."
    ):
        validator.validate(invalid_shorturl)
