import pytest
from datetime import datetime, timezone

from shortener.domain.shorturl import ShortURL, Slug, URL


@pytest.fixture
def shorturl(normal_shorturl):
    return normal_shorturl


def test_set_id_raises_attribute_error(shorturl: ShortURL):
    with pytest.raises(
        AttributeError, 
        match="property 'id' of 'ShortURL' object has no setter"
    ):
        shorturl.id = 3


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


def test_set_owner_id(shorturl: ShortURL):
    shorturl.owner_id = 3
    assert shorturl.owner_id == 3


def test_set_owner_id_raises_type_error(shorturl: ShortURL):
    with pytest.raises(TypeError):
        shorturl.owner_id = "4"


def test_set_is_active_raises_attribute_error(shorturl: ShortURL):
    with pytest.raises(
        AttributeError, 
        match="property 'is_active' of 'ShortURL' object has no setter"
    ):
        shorturl.is_active = True


def test_set_visit_count(shorturl: ShortURL):
    shorturl.visit_count = 3
    assert shorturl.visit_count == 3


def test_set_visit_count_raises_type_error(shorturl: ShortURL):
    with pytest.raises(TypeError):
        shorturl.visit_count = "4"


def test_set_created_at(shorturl: ShortURL):
    date = datetime(2000, 12, 12, tzinfo=timezone.utc)
    shorturl.created_at = date
    assert shorturl.created_at == date


def test_set_created_at_raises_type_error(shorturl: ShortURL):
    with pytest.raises(TypeError):
        shorturl.created_at = 2002


def test_set_expires_at(shorturl: ShortURL):
    date = datetime(2000, 12, 12, tzinfo=timezone.utc)
    shorturl.expires_at = date
    assert shorturl.expires_at == date


def test_set_expires_at_raises_type_error(shorturl: ShortURL):
    with pytest.raises(TypeError):
        shorturl.expires_at = 2002


def test_set_last_accessed_at(shorturl: ShortURL):
    date = datetime(2000, 12, 12, tzinfo=timezone.utc)
    shorturl.last_accessed_at = date
    assert shorturl.last_accessed_at == date


def test_set_last_accessed_at_raises_type_error(shorturl: ShortURL):
    with pytest.raises(TypeError):
        shorturl.last_accessed_at = 2002
