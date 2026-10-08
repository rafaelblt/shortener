import pytest
from datetime import datetime, timedelta, timezone
from uuid import UUID

from shortener.domain.shorturl import ShortURL
from shortener.domain.shorturl import (
    Slug, TargetURL, ShortURLStatus, ShortURLID, OwnerID
)


ID_VALUE = UUID("0199b2c4-7a3e-7c1a-9b5e-3f2d4c6b8a10")
OWNER_ID_VALUE = UUID("0199b2c4-7a3e-7c1a-9b5e-3f2d4c6b8a11")


@pytest.fixture
def shorturl():
    return ShortURL.restore(
        id=ShortURLID(ID_VALUE),
        slug=Slug("i-am-slug"),
        target_url=TargetURL("https://google.com"),
        owner_id=OwnerID(OWNER_ID_VALUE),
        status=ShortURLStatus.DEACTIVATED,
        resolution_count=5,
        created_at=datetime(year=2002, month=2, day=2, tzinfo=timezone.utc),
        expires_at=datetime(year=2006, month=6, day=6, tzinfo=timezone.utc),
        last_resolved_at=datetime(year=2004, month=4, day=4, tzinfo=timezone.utc)
    )


def test_instance(shorturl: ShortURL):
    assert isinstance(shorturl, ShortURL)


def test_id(shorturl: ShortURL):
    assert shorturl.id == ShortURLID(ID_VALUE)


def test_slug(shorturl: ShortURL):
    assert isinstance(shorturl.slug, Slug)
    assert shorturl.slug == "i-am-slug"


def test_target_url(shorturl: ShortURL):
    assert isinstance(shorturl.target_url, TargetURL)
    assert shorturl.target_url == "https://google.com"


def test_owner_id(shorturl: ShortURL):
    assert shorturl.owner_id == OwnerID(OWNER_ID_VALUE)


def test_status(shorturl: ShortURL):
    assert shorturl.status == ShortURLStatus.DEACTIVATED


def test_resolution_count(shorturl: ShortURL):
    assert shorturl.resolution_count == 5


def test_created_at(shorturl: ShortURL):
    created_at = shorturl.created_at
    expected = datetime(2002, 2, 2)
    strftime = "%d/%m/%Y, %H:%M:%S"

    assert isinstance(created_at, datetime)
    assert created_at.strftime(strftime) == expected.strftime(strftime)


def test_expires_at(shorturl: ShortURL):
    expires_at = shorturl.expires_at
    expected = datetime(2006, 6, 6)
    strftime = "%d/%m/%Y, %H:%M:%S"

    assert isinstance(expires_at, datetime)
    assert expires_at.strftime(strftime) == expected.strftime(strftime)


def test_last_resolved_at(shorturl: ShortURL):
    last_resolved_at = shorturl.last_resolved_at
    expected = datetime(2004, 4, 4)
    strftime = "%d/%m/%Y, %H:%M:%S"

    assert isinstance(last_resolved_at, datetime)
    assert last_resolved_at.strftime(strftime) == expected.strftime(strftime)


def test_keeps_datetimes_in_any_timezone(shorturl: ShortURL):
    naive = datetime(year=2002, month=2, day=2)
    other_timezone = datetime(year=2006, month=6, day=6, tzinfo=timezone(timedelta(hours=-3)))
    restored = ShortURL.restore(
        id=shorturl.id,
        slug=shorturl.slug,
        target_url=shorturl.target_url,
        owner_id=shorturl.owner_id,
        status=shorturl.status,
        resolution_count=shorturl.resolution_count,
        created_at=naive,
        expires_at=other_timezone,
        last_resolved_at=None,
    )
    assert restored.created_at == naive
    assert restored.expires_at == other_timezone
