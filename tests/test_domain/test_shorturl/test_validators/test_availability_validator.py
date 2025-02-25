from datetime import datetime, timezone

from pytest import fixture, raises

from shortener.domain.shorturl import ShortURL
from shortener.domain.shorturl.exceptions import InactiveShortURL, ShortURLExpired
from shortener.domain.shorturl.validators import AvailabilityValidator


@fixture
def validator():
    return AvailabilityValidator()


def test_validate_normal_shorturl(validator, normal_shorturl):
    validator.validate(normal_shorturl)


def test_validate_with_is_active_false(validator):
    shorturl = ShortURL(
        slug="example", original_url="test.com", is_active=False
    )
    with raises(InactiveShortURL, match="The ShortURL is not active"):
        validator.validate(shorturl)


def test_validate_with_valid_expires_at(validator):
    shorturl = ShortURL(
        slug="example",
        original_url="test.com", 
        expires_at=datetime(year=3950, month=1, day=1, tzinfo=timezone.utc)
    )
    validator.validate(shorturl)


def test_validate_with_invalid_expires_at(validator):
    shorturl = ShortURL(
        slug="example", 
        original_url="test.com", 
        expires_at=datetime(year=2020, month=1, day=1, tzinfo=timezone.utc)
    )
    with raises(ShortURLExpired, match="The ShortURL has expired."):
        validator.validate(shorturl)
