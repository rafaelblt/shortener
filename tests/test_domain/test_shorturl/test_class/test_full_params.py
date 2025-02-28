from datetime import datetime, timezone

from shortener.domain.shorturl import ShortURL

from pytest import fixture


@fixture
def shorturl():
    return ShortURL(
        id=1,
        slug="i-am-url",
        original_url="google.com",
        owner_id=1,
        is_active=False,
        visit_count=5,
        created_at=datetime(year=2002, month=2, day=2),
        expires_at=datetime(year=2006, month=6, day=6),
        last_accessed_at=datetime(year=2004, month=4, day=4)
    )


def test_instance(shorturl):
    assert isinstance(shorturl, ShortURL)


def test_id(shorturl):
    assert shorturl.id == 1


def test_slug(shorturl):
    assert shorturl.slug == "i-am-url"


def test_original_url(shorturl):
    assert shorturl.original_url == "google.com"


def test_owner_id(shorturl):
    assert shorturl.owner_id == 1


def test_is_active(shorturl):
    assert shorturl.is_active == False


def test_visit_count(shorturl):
    assert shorturl.visit_count == 5


def test_created_at(shorturl):
    created_at = shorturl.created_at
    expected = datetime(2002, 2, 2)

    assert isinstance(created_at, datetime)
    assert created_at.year == expected.year
    assert created_at.month == expected.month
    assert created_at.day == expected.day
    assert created_at.hour == expected.hour


def test_expires_at(shorturl):
    expires_at = shorturl.expires_at
    expected = datetime(2006, 6, 6)

    assert isinstance(expires_at, datetime)
    assert expires_at.year == expected.year
    assert expires_at.month == expected.month
    assert expires_at.day == expected.day
    assert expires_at.hour == expected.hour


def test_last_accessed_at(shorturl):
    last_accessed_at = shorturl.last_accessed_at
    expected = datetime(2004, 4, 4)

    assert isinstance(last_accessed_at, datetime)
    assert last_accessed_at.year == expected.year
    assert last_accessed_at.month == expected.month
    assert last_accessed_at.day == expected.day
    assert last_accessed_at.hour == expected.hour
