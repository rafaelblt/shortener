import pytest

from shortener.domain.shorturl import ShortURL
from shortener.domain.shorturl.fields import Slug, URL


@pytest.fixture
def valid_slug():
    return Slug("valid-slug")


@pytest.fixture
def valid_url():
    return URL("https://valid-url.com")


def get_type_error_message(attr, type_expected, got):
    return (
        f"The ShortURL {attr} must be an instance of {type_expected}, got "
        f"{type(got).__name__}"
    )


def test_slug_invalid(valid_url: URL):
    slug = {"slug": "test-slug"}
    e = get_type_error_message(attr="slug", type_expected="Slug", got=slug)
    with pytest.raises(TypeError, match=e):
        ShortURL(slug=slug, original_url=valid_url)      


def test_original_url_invalid(valid_slug: Slug):
    url = "https://github.com"
    e = get_type_error_message(attr="original_url", type_expected="URL", got=url)
    with pytest.raises(TypeError, match=e):
        ShortURL(slug=valid_slug, original_url=url)
    

def test_id_invalid(valid_slug: Slug, valid_url: URL):
    id = "1"
    e = get_type_error_message(attr="id", type_expected="int or None", got=id)
    with pytest.raises(TypeError, match=e):
        ShortURL(slug=valid_slug, original_url=valid_url, id=id)
    

def test_owner_invalid(valid_slug: Slug, valid_url: URL): 
    owner = 1
    e = get_type_error_message(
        attr="owner", type_expected="User or None", got=owner
    )
    with pytest.raises(TypeError, match=e):
        ShortURL(slug=valid_slug, original_url=valid_url, owner=owner)


def test_status_invalid(valid_slug: Slug, valid_url: URL): 
    status = "active"
    e = get_type_error_message(
        attr="status", type_expected="ShortURLStatus", got=status
    )
    with pytest.raises(TypeError, match=e):
        ShortURL(slug=valid_slug, original_url=valid_url, status=status)


def test_visit_count_invalid(valid_slug: Slug, valid_url: URL): 
    visit_count = "1"
    e = get_type_error_message(
        attr="visit_count", type_expected="int", got=visit_count
    )
    with pytest.raises(TypeError, match=e):
        ShortURL(slug=valid_slug, original_url=valid_url, visit_count=visit_count)


def test_created_at_invalid(valid_slug: Slug, valid_url: URL): 
    created_at = 1992
    e = get_type_error_message(
        attr="created_at", type_expected="datetime", got=created_at
    )
    with pytest.raises(TypeError, match=e):
        ShortURL(slug=valid_slug, original_url=valid_url, created_at=created_at)


def test_expires_at_invalid(valid_slug: Slug, valid_url: URL): 
    expires_at = 1992
    e = get_type_error_message(
        attr="expires_at", type_expected="datetime or None", got=expires_at
    )
    with pytest.raises(TypeError, match=e):
        ShortURL(slug=valid_slug, original_url=valid_url, expires_at=expires_at)


def test_last_accessed_at_invalid(valid_slug: Slug, valid_url: URL): 
    last_accessed_at = 1992
    e = get_type_error_message(
        attr="last_accessed_at", 
        type_expected="datetime or None", 
        got=last_accessed_at
    )
    with pytest.raises(TypeError, match=e):
        ShortURL(
            slug=valid_slug, 
            original_url=valid_url, 
            last_accessed_at=last_accessed_at
        )


def test_visist_count_lower_than_0(valid_slug: Slug, valid_url: URL):
    visit_count = -1
    e = ("The ShortURL visit_count must be greater than or equal to 0, "
        f"got {visit_count}")
    with pytest.raises(ValueError, match=e):
        ShortURL(slug=valid_slug, original_url=valid_url, visit_count=visit_count)
