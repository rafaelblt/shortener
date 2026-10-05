import pytest

from datetime import datetime, timezone
from uuid import UUID

from shortener.domain.shorturl.shorturl import ShortURL
from shortener.domain.shorturl.fields import OriginalURL, Slug, ShortURLID, OwnerID


@pytest.fixture
def owner_id():
    return OwnerID(UUID("0199b2c4-7a3e-7c1a-9b5e-3f2d4c6b8a10"))


@pytest.fixture
def normal_shorturl(owner_id):
    return ShortURL.create(
        slug=Slug("lorem-ipsum-website"),
        original_url=OriginalURL("https://lorem.makeyoursite.com"),
        owner_id=owner_id,
    )


@pytest.fixture
def other_shorturl(owner_id):
    return ShortURL.create(
        slug=Slug("other-network"),
        original_url=OriginalURL("https://others.com"),
        owner_id=owner_id,
    )


@pytest.fixture
def old_shorturl(owner_id):
    return ShortURL(
        id=ShortURLID.generate(),
        slug=Slug("old-site"),
        original_url=OriginalURL("https://google.com"),
        owner_id=owner_id,
        created_at=datetime(year=2000, month=1, day=1, tzinfo=timezone.utc)
    )


@pytest.fixture
def expired_shorturl(owner_id):
    return ShortURL.create(
        slug=Slug("this-is-expired"),
        original_url=OriginalURL("https://expiration.com"),
        owner_id=owner_id,
        expires_at=datetime(year=2000, month=1, day=1, tzinfo=timezone.utc)
    )


@pytest.fixture
def biggest_shorturl(owner_id):
    return ShortURL.create(
        slug=Slug("the-top-one"),
        original_url=OriginalURL("https://bigbig.com"),
        owner_id=owner_id,
    )
