import pytest
from datetime import datetime

from shortener.domain.shorturl import ShortURL
from shortener.domain.shorturl.fields import ShortURLStatus, ShortURLID, OwnerID


@pytest.fixture
def shorturl(normal_shorturl):
    return normal_shorturl


def test_instance(shorturl: ShortURL):
    assert isinstance(shorturl, ShortURL)


def test_id(shorturl: ShortURL):
    assert isinstance(shorturl.id, ShortURLID)


def test_each_shorturl_gets_its_own_id(shorturl: ShortURL, other_shorturl: ShortURL):
    assert shorturl.id != other_shorturl.id


def test_owner_id(shorturl: ShortURL, owner_id: OwnerID):
    assert shorturl.owner_id == owner_id


def test_slug(shorturl: ShortURL):
    assert shorturl.slug == "lorem-ipsum-website"


def test_target_url(shorturl: ShortURL):
    assert shorturl.target_url == "https://lorem.makeyoursite.com"


def test_status(shorturl: ShortURL):
    assert shorturl.status == ShortURLStatus.ACTIVE


def test_visit_count(shorturl: ShortURL):
    assert shorturl.visit_count == 0


def test_created_at_is_the_given_now(shorturl: ShortURL, now: datetime):
    assert shorturl.created_at == now


def test_expires_at(shorturl: ShortURL):
    assert shorturl.expires_at == None


def test_last_accessed_at(shorturl: ShortURL):
    assert shorturl.last_accessed_at == None
