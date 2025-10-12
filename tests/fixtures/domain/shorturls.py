import pytest

from datetime import datetime, timezone

from shortener.domain.shorturl.shorturl import ShortURL
from shortener.domain.shorturl.fields import OriginalURL, Slug


@pytest.fixture
def normal_shorturl():
    return ShortURL(
        slug=Slug("lorem-ipsum-website"),
        original_url=OriginalURL("https://lorem.makeyoursite.com"),
    )


@pytest.fixture
def other_shorturl():
    return ShortURL(
        slug=Slug("other-network"),
        original_url=OriginalURL("https://others.com"),
    )


@pytest.fixture
def old_shorturl():
    return ShortURL(
        slug=Slug("old-site"),
        original_url=OriginalURL("https://google.com"),
        created_at=datetime(year=2000, month=1, day=1, tzinfo=timezone.utc)
    )


@pytest.fixture
def expired_shorturl():
    return ShortURL(
        slug=Slug("this-is-expired"),
        original_url=OriginalURL("https://expiration.com"),
        expires_at=datetime(year=2000, month=1, day=1, tzinfo=timezone.utc)
    )


@pytest.fixture
def biggest_shorturl():
    return ShortURL(
        slug=Slug("the-top-one"),
        original_url=OriginalURL("https://bigbig.com"),
    )
