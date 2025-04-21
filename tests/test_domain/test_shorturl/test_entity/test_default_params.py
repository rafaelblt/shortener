import pytest
from datetime import datetime, timezone

from shortener.domain.shorturl import ShortURL
from shortener.domain.shorturl.fields import ShortURLStatus


@pytest.fixture
def shorturl(normal_shorturl):
    return normal_shorturl


def test_instance(shorturl: ShortURL):
    assert isinstance(shorturl, ShortURL)


def test_id(shorturl: ShortURL):
    assert shorturl.id == None


def test_slug(shorturl: ShortURL):
    assert shorturl.slug == "lorem-ipsum-website"


def test_original_url(shorturl: ShortURL):
    assert shorturl.original_url == "https://lorem.makeyoursite.com"


def test_owner(shorturl: ShortURL, normal_user):
    assert shorturl.owner == normal_user


def test_status(shorturl: ShortURL):
    assert shorturl.status == ShortURLStatus.ACTIVE


def test_visit_count(shorturl: ShortURL):
    assert shorturl.visit_count == 0


def test_created_at(shorturl: ShortURL):
    created_at = shorturl.created_at
    expected = datetime.now(tz=timezone.utc)
    strftime = "%d/%m/%Y, %H:%M:%S"

    assert isinstance(created_at, datetime)
    assert created_at.strftime(strftime) == expected.strftime(strftime)


def test_expires_at(shorturl: ShortURL):
    assert shorturl.expires_at == None


def test_last_accessed_at(shorturl: ShortURL):
    assert shorturl.last_accessed_at == None
