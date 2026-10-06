import pytest

from datetime import datetime, timedelta, timezone
from uuid import UUID

from shortener.domain.shorturl.shorturl import ShortURL
from shortener.domain.shorturl.fields import TargetURL, Slug, ShortURLID, OwnerID


@pytest.fixture
def now():
    return datetime(year=2026, month=1, day=1, tzinfo=timezone.utc)


@pytest.fixture
def owner_id():
    return OwnerID(UUID("0199b2c4-7a3e-7c1a-9b5e-3f2d4c6b8a10"))


@pytest.fixture
def normal_shorturl(owner_id, now):
    return ShortURL.create(
        slug=Slug("lorem-ipsum-website"),
        target_url=TargetURL("https://lorem.makeyoursite.com"),
        owner_id=owner_id,
        now=now,
    )


@pytest.fixture
def other_shorturl(owner_id, now):
    return ShortURL.create(
        slug=Slug("other-network"),
        target_url=TargetURL("https://others.com"),
        owner_id=owner_id,
        now=now,
    )


@pytest.fixture
def old_shorturl(owner_id):
    return ShortURL(
        id=ShortURLID.generate(),
        slug=Slug("old-site"),
        target_url=TargetURL("https://google.com"),
        owner_id=owner_id,
        created_at=datetime(year=2000, month=1, day=1, tzinfo=timezone.utc)
    )


@pytest.fixture
def expired_shorturl(owner_id, now):
    return ShortURL.create(
        slug=Slug("this-is-expired"),
        target_url=TargetURL("https://expiration.com"),
        owner_id=owner_id,
        now=now - timedelta(days=2),
        expires_at=now - timedelta(days=1),
    )


@pytest.fixture
def biggest_shorturl(owner_id, now):
    return ShortURL.create(
        slug=Slug("the-top-one"),
        target_url=TargetURL("https://bigbig.com"),
        owner_id=owner_id,
        now=now,
    )


@pytest.fixture
def expires_at(now):
    return now + timedelta(hours=1)


@pytest.fixture
def expiring_shorturl(owner_id, now, expires_at):
    return ShortURL.create(
        slug=Slug("expires-soon"),
        target_url=TargetURL("https://soon.com"),
        owner_id=owner_id,
        now=now,
        expires_at=expires_at,
    )
