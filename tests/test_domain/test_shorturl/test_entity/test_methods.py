import pytest
from datetime import datetime, timezone

from shortener.domain.shorturl import ShortURL, Slug, URL
from shortener.domain.shorturl.exceptions import ShortURLInactiveError, ShortURLExpiredError


def test_record_visit(normal_shorturl: ShortURL):
    expected_visit_count = normal_shorturl.visit_count + 1
    expected_last_accessed_at = datetime.now(tz=timezone.utc)
    strftime = "%d/%m/%Y %H:%M:%S"

    normal_shorturl.record_visit()

    assert normal_shorturl.visit_count == expected_visit_count
    assert (
        normal_shorturl.last_accessed_at.strftime(strftime) == 
        expected_last_accessed_at.strftime(strftime)
    )


def test_resolve(normal_shorturl: ShortURL):
    assert normal_shorturl.resolve() == normal_shorturl.original_url


def test_resolve_raises_inactive_error(normal_shorturl: ShortURL):
    normal_shorturl._disable()
    with pytest.raises(ShortURLInactiveError):
        normal_shorturl.resolve()


def test_resolve_raises_expired_error(expired_shorturl: ShortURL):
    with pytest.raises(ShortURLExpiredError):
        expired_shorturl.resolve()
