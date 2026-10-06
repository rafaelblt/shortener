import pytest
from datetime import datetime

from shortener.domain.shorturl import ShortURL
from shortener.domain.shorturl.fields import ShortURLStatus
from shortener.domain.shorturl.exceptions import (
    ShortURLDeactivatedError, 
    ShortURLExpiredError
)


def test_record_visit_increments_the_visit_count(normal_shorturl: ShortURL, now: datetime):
    normal_shorturl.record_visit(now)
    assert normal_shorturl.visit_count == 1


def test_record_visit_sets_last_accessed_at_to_now(normal_shorturl: ShortURL, now: datetime):
    normal_shorturl.record_visit(now)
    assert normal_shorturl.last_accessed_at == now


def test_record_visit_rejects_a_datetime_outside_utc(normal_shorturl: ShortURL):
    with pytest.raises(ValueError, match="must be in UTC"):
        normal_shorturl.record_visit(datetime(year=2026, month=1, day=1))


def test_resolve(normal_shorturl: ShortURL, now: datetime):
    assert normal_shorturl.resolve(now) == normal_shorturl.target_url


def test_resolve_raises_deactivated_error(normal_shorturl: ShortURL, now: datetime):
    normal_shorturl.disable()
    with pytest.raises(ShortURLDeactivatedError):
        normal_shorturl.resolve(now)


def test_resolve_raises_expired_error(expired_shorturl: ShortURL, now: datetime):
    with pytest.raises(ShortURLExpiredError):
        expired_shorturl.resolve(now)


def test_resolve_raises_expired_error_once_expires_at_is_reached(
    expiring_shorturl: ShortURL, now: datetime, expires_at: datetime
):
    assert expiring_shorturl.resolve(now) == expiring_shorturl.target_url
    with pytest.raises(ShortURLExpiredError):
        expiring_shorturl.resolve(expires_at)


def test_resolve_raises_deactivated_error_when_also_expired(
    expired_shorturl: ShortURL, now: datetime
):
    expired_shorturl.disable()
    with pytest.raises(ShortURLDeactivatedError):
        expired_shorturl.resolve(now)


def test_disable_deactivates_an_active_shorturl(normal_shorturl: ShortURL):
    normal_shorturl.disable()
    assert normal_shorturl.status == ShortURLStatus.DEACTIVATED


def test_disable_keeps_a_deactivated_shorturl_deactivated(normal_shorturl: ShortURL):
    normal_shorturl.disable()
    normal_shorturl.disable()
    assert normal_shorturl.status == ShortURLStatus.DEACTIVATED


def test_enable_activates_a_deactivated_shorturl(normal_shorturl: ShortURL):
    normal_shorturl.disable()
    normal_shorturl.enable()
    assert normal_shorturl.status == ShortURLStatus.ACTIVE


def test_enable_keeps_an_active_shorturl_active(normal_shorturl: ShortURL):
    normal_shorturl.enable()
    assert normal_shorturl.status == ShortURLStatus.ACTIVE
