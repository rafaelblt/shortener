import pytest

from datetime import datetime, timezone

from shortener.domain.shorturl.shorturl import ShortURL
from shortener.domain.shorturl.fields import URL, Slug


@pytest.fixture
def normal_shorturl(normal_user):
    return ShortURL(
        slug=Slug("lorem-ipsum-website"),
        original_url=URL("https://lorem.makeyoursite.com"),
        owner=normal_user
    )


@pytest.fixture
def other_shorturl(normal_user):
    return ShortURL(
        slug=Slug("other-network"),
        original_url=URL("https://others.com"),
        owner=normal_user
    )


@pytest.fixture
def old_shorturl(old_user):
    return ShortURL(
        slug=Slug("old-site"),
        original_url=URL("https://google.com"),
        owner=old_user,
        created_at=datetime(year=2000, month=1, day=1, tzinfo=timezone.utc)
    )


@pytest.fixture
def expired_shorturl(normal_user):
    return ShortURL(
        slug=Slug("this-is-expired"),
        original_url=URL("https://expiration.com"),
        owner=normal_user,
        expires_at=datetime(year=2000, month=1, day=1, tzinfo=timezone.utc)
    )
