from datetime import datetime, timezone

from pytest import fixture, raises

from shortener.domain.shorturl import ShortURL
from shortener.domain.shorturl.exceptions import (
    ShortURLInactiveError, ShortURLExpiredError
)


@fixture
def validator(shorturl_availability_validator):
    return shorturl_availability_validator


def test_validate_normal_shorturl(validator, normal_shorturl):
    validator.validate(normal_shorturl)


def test_validate_with_is_active_false(validator, normal_shorturl):
    normal_shorturl.is_active = False
    with raises(ShortURLInactiveError, match="The ShortURL is not active"):
        validator.validate(normal_shorturl)


def test_validate_with_valid_expires_at(validator, normal_shorturl):
    normal_shorturl.expires_at = datetime(
        year=3950, month=1, day=1, tzinfo=timezone.utc
    )
    validator.validate(normal_shorturl)


def test_validate_with_invalid_expires_at(validator, normal_shorturl):
    normal_shorturl.expires_at = datetime(
        year=2020, month=1, day=1, tzinfo=timezone.utc
    )
    with raises(ShortURLExpiredError, match="The ShortURL has expired."):
        validator.validate(normal_shorturl)
