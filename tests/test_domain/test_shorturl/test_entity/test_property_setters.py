import pytest
from datetime import datetime, timezone

from shortener.domain.shorturl import ShortURL
from shortener.domain.shorturl.fields import Slug, URL, ShortURLStatus


@pytest.fixture
def shorturl(normal_shorturl):
    return normal_shorturl


def test_set_slug(shorturl: ShortURL):
    shorturl.slug = Slug("test-new-slug")
    assert shorturl.slug == "test-new-slug"


def test_set_slug_raises_type_error(shorturl: ShortURL):
    with pytest.raises(TypeError):
        shorturl.slug = "test-new-slug"


def test_set_original_url(shorturl: ShortURL): 
    shorturl.original_url = URL("https://test-new-url.com")
    assert shorturl.original_url == "https://test-new-url.com"


def test_set_original_url_raises_type_error(shorturl: ShortURL): 
    with pytest.raises(TypeError):
        shorturl.original_url = "https://superhero.com"


def test_set_owner_raises_attribute_error(shorturl: ShortURL):
    with pytest.raises(
        AttributeError, 
        match="property 'owner' of 'ShortURL' object has no setter"
    ):
        shorturl.owner = 4


def test_set_status_raises_attribute_error(shorturl: ShortURL):
    with pytest.raises(
        AttributeError, 
        match="property 'status' of 'ShortURL' object has no setter"
    ):
        shorturl.status = ShortURLStatus.BANNED


def test_set_visit_count_raises_attribute_error(shorturl: ShortURL):
    with pytest.raises(
        AttributeError, 
        match="property 'visit_count' of 'ShortURL' object has no setter"
    ):
        shorturl.visit_count = 3


def test_set_created_at_raises_attribute_error(shorturl: ShortURL):
    with pytest.raises(
        AttributeError, 
        match="property 'created_at' of 'ShortURL' object has no setter"
    ):
        shorturl.created_at = 2002


def test_set_expires_at_raises_attribute_error(shorturl: ShortURL):
    with pytest.raises(
        AttributeError, 
        match="property 'expires_at' of 'ShortURL' object has no setter"
    ):
        shorturl.expires_at = 2002


def test_set_last_accessed_at_raises_attribute_error(shorturl: ShortURL):
    with pytest.raises(
        AttributeError, 
        match="property 'last_accessed_at' of 'ShortURL' object has no setter"
    ):
        shorturl.last_accessed_at = 2002
