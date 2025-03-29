import pytest

from shortener.domain.shorturl import ShortURL, Slug, URL


@pytest.fixture
def valid_slug():
    return Slug("valid-slug")


@pytest.fixture
def valid_url():
    return URL("valid-url")


def test_slug_invalid(valid_url: URL):
    slug = {"slug": "test-slug"}
    e = f"The ShortURL slug must be an instance of Slug, got {dict.__name__}"
    with pytest.raises(TypeError, match=e):
        ShortURL(slug=slug, original_url=valid_url)      


def test_original_url_invalid(valid_slug: Slug):
    url = "https://github.com"
    e = f"The ShortURL original_url must be an instance of URL, got {str.__name__}"
    with pytest.raises(TypeError, match=e):
        ShortURL(slug=valid_slug, original_url=url)
    

def test_id_invalid(valid_slug: Slug, valid_url: URL):
    id = "1"
    e = f"The ShortURL id must be int or None, got {str.__name__}"
    with pytest.raises(TypeError, match=e):
        ShortURL(slug=valid_slug, original_url=valid_url, id=id)
    

def test_owner_id_invalid(valid_slug: Slug, valid_url: URL): 
    owner_id = [1]
    e = f"The ShortURL owner_id must be int or None, got {list.__name__}"
    with pytest.raises(TypeError, match=e):
        ShortURL(slug=valid_slug, original_url=valid_url, owner_id=owner_id)


def test_is_active_invalid(valid_slug: Slug, valid_url: URL): 
    is_active = 1
    e = f"The ShortURL is_active must be bool, got {int.__name__}"
    with pytest.raises(TypeError, match=e):
        ShortURL(slug=valid_slug, original_url=valid_url, is_active=is_active)


def test_visit_count_invalid(valid_slug: Slug, valid_url: URL): 
    visit_count = "1"
    e = f"The ShortURL visit_count must be int, got {str.__name__}"
    with pytest.raises(TypeError, match=e):
        ShortURL(slug=valid_slug, original_url=valid_url, visit_count=visit_count)


def test_created_at_invalid(valid_slug: Slug, valid_url: URL): 
    created_at = 1992
    e = (
        f"The ShortURL created_at must be an instance of datetime or None, "
        f"got {int.__name__}"
    )
    with pytest.raises(TypeError, match=e):
        ShortURL(slug=valid_slug, original_url=valid_url, created_at=created_at)


def test_expires_at_invalid(valid_slug: Slug, valid_url: URL): 
    expires_at = 1992
    e = (
        f"The ShortURL expires_at must be an instance of datetime or None, "
        f"got {int.__name__}"
    )
    with pytest.raises(TypeError, match=e):
        ShortURL(slug=valid_slug, original_url=valid_url, expires_at=expires_at)


def test_last_accessed_at_invalid(valid_slug: Slug, valid_url: URL): 
    last_accessed_at = 1992
    e = (
        f"The ShortURL last_accessed_at must be an instance of datetime or None, "
        f"got {int.__name__}"
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
    with pytest.raises(TypeError, match=e):
        ShortURL(slug=valid_slug, original_url=valid_url, visit_count=visit_count)
