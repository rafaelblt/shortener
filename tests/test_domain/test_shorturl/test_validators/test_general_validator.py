from pytest import fixture, raises

from shortener.domain.shorturl import ShortURL
from shortener.domain.shorturl.validators import GeneralValidator
from shortener.domain.shorturl.exceptions import (
    InvalidSlugException, SlugAlreadyExistsException
)


@fixture
def validator(mock_repository):
    return GeneralValidator(repository=mock_repository)


def test_validate_valid_slug(validator):
    assert validator._validate_slug("my-short-url") == None


def test_validate_invalid_slug(validator):
    with raises(InvalidSlugException, match="The provided slug is forbidden."):
        validator._validate_slug("api")


def test_validate_already_exist_slug(validator):
    with raises(
        SlugAlreadyExistsException, match="The provided slug already exists."
    ):
        validator._validate_slug("joker")


def test_validate_valid_shorturl(validator, normal_shorturl):
    assert validator.validate(normal_shorturl) == None


def test_validate_invalid_shorturl(validator):
    invalid_shorturl = ShortURL(slug="config", original_url="virus.com")
    with raises(InvalidSlugException, match="The provided slug is forbidden."):
        validator.validate(invalid_shorturl)
