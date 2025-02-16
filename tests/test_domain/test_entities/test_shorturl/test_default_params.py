from datetime import datetime, timezone

from shortener.domain.shorturl import ShortURL

from pytest import fixture


@fixture
def shorturl():
    return ShortURL(
        slug="my-url",
        original_url="youtube.com",
    )


def test_slug(shorturl):
    assert shorturl.slug == "my-url"


def test_original_url(shorturl):
    assert shorturl.original_url == "youtube.com"


def test_owner_id(shorturl):
    assert shorturl.owner_id == None


def test_is_active(shorturl):
    assert shorturl.is_active == True


def test_visit_count(shorturl):
    assert shorturl.visit_count == 0


def test_created_at(shorturl):
    created_at = shorturl.created_at
    now = datetime.now(tz=timezone.utc)

    assert isinstance(created_at, datetime)
    assert created_at.year == now.year
    assert created_at.month == now.month
    assert created_at.day == now.day
    assert created_at.hour == now.hour


def test_expires_at(shorturl):
    assert shorturl.expires_at == None


def test_last_accessed_at(shorturl):
    assert shorturl.last_accessed_at == None
