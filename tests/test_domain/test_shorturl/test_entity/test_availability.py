from datetime import datetime, timedelta

from shortener.domain.shorturl import ShortURL


def test_is_not_expired_without_expires_at(normal_shorturl: ShortURL, now: datetime):
    assert normal_shorturl.is_expired(now) is False


def test_is_not_expired_before_expires_at(expiring_shorturl: ShortURL, now: datetime):
    assert expiring_shorturl.is_expired(now) is False


def test_is_expired_at_expires_at(expiring_shorturl: ShortURL, expires_at: datetime):
    assert expiring_shorturl.is_expired(expires_at) is True


def test_is_expired_after_expires_at(expiring_shorturl: ShortURL, expires_at: datetime):
    assert expiring_shorturl.is_expired(expires_at + timedelta(days=1)) is True


def test_is_available_when_active_and_not_expired(normal_shorturl: ShortURL, now: datetime):
    assert normal_shorturl.is_available(now) is True


def test_is_not_available_when_expired(expired_shorturl: ShortURL, now: datetime):
    assert expired_shorturl.is_available(now) is False


def test_is_not_available_when_deactivated(normal_shorturl: ShortURL, now: datetime):
    normal_shorturl.disable()
    assert normal_shorturl.is_available(now) is False
