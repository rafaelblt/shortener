from pytest import fixture, raises

from shortener.domain.shorturl import ShortURL
from shortener.domain.shorturl import exceptions
from shortener.domain.shorturl.validators import GeneralShortURLValidator


@fixture
def validator(mock_repository):
    return GeneralShortURLValidator(repository=mock_repository)

@fixture
def shorturl():
    return ShortURL(
        slug="my-url",
        original_url="youtube.com"
    )

@fixture
def invalid_shorturl():
    return ShortURL(
        slug="config",
        original_url="virus.com"
    )


def test_validate_valid_slug(validator):
    assert validator._validate_slug("my-short-url") == None


def test_validate_invalid_slug(validator):
    with raises(exceptions.InvalidSlugException):
        validator._validate_slug("api")


def test_validate_already_exist_slug(validator):
    with raises(exceptions.SlugAlreadyExistsException):
        validator._validate_slug("joker")


def test_validate_valid_shorturl(validator, shorturl):
    assert validator.validate(shorturl) == None


def test_validate_invalid_shorturl(validator, invalid_shorturl):
    with raises(exceptions.InvalidSlugException):
        validator.validate(invalid_shorturl)
