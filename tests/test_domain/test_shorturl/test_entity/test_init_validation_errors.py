import pytest

from shortener.domain.shorturl import ShortURL
from shortener.domain.shorturl.fields import Slug, OriginalURL


@pytest.fixture
def valid_slug():
    return Slug("valid-slug")


@pytest.fixture
def valid_url():
    return OriginalURL("https://valid-url.com")


@pytest.fixture
def required_fields(normal_shorturl):
    return {
        "id": normal_shorturl.id,
        "slug": normal_shorturl.slug,
        "original_url": normal_shorturl.original_url,
        "owner_id": normal_shorturl.owner_id,
        "created_at": normal_shorturl.created_at,
    }


def get_type_error_message(attr, type_expected, got):
    return (
        f"The ShortURL {attr} must be an instance of {type_expected}, got "
        f"{type(got).__name__}"
    )


def test_slug_invalid(required_fields: dict):
    required_fields.pop("slug")
    slug = {"slug": "test-slug"}
    e = get_type_error_message(attr="slug", type_expected="Slug", got=slug)
    with pytest.raises(TypeError, match=e):
        ShortURL(**required_fields, slug=slug) # type: ignore


def test_original_url_invalid(required_fields: dict):
    required_fields.pop("original_url")
    url = "https://github.com"
    e = get_type_error_message(attr="original_url", type_expected="OriginalURL", got=url)
    with pytest.raises(TypeError, match=e):
        ShortURL(**required_fields, original_url=url) # type: ignore
    

def test_id_invalid(required_fields: dict):
    required_fields.pop("id")
    id = 1
    e = get_type_error_message(attr="id", type_expected="ShortURLID", got=id)
    with pytest.raises(TypeError, match=e):
        ShortURL(**required_fields, id=id) # type: ignore


def test_owner_id_invalid(required_fields: dict):
    required_fields.pop("owner_id")
    owner_id = 1
    e = get_type_error_message(attr="owner_id", type_expected="OwnerID", got=owner_id)
    with pytest.raises(TypeError, match=e):
        ShortURL(**required_fields, owner_id=owner_id) # type: ignore


def test_status_invalid(required_fields: dict): 
    status = "active"
    e = get_type_error_message(
        attr="status", type_expected="ShortURLStatus", got=status
    )
    with pytest.raises(TypeError, match=e):
        ShortURL(**required_fields, status=status) # type: ignore


def test_visit_count_invalid(required_fields: dict): 
    visit_count = "1"
    e = get_type_error_message(
        attr="visit_count", type_expected="int", got=visit_count
    )
    with pytest.raises(TypeError, match=e):
        ShortURL(**required_fields, visit_count=visit_count) # type: ignore


def test_created_at_invalid(required_fields: dict): 
    required_fields.pop("created_at")
    created_at = 1992
    e = get_type_error_message(
        attr="created_at", type_expected="datetime", got=created_at
    )
    with pytest.raises(TypeError, match=e):
        ShortURL(**required_fields, created_at=created_at) # type: ignore


def test_expires_at_invalid(required_fields: dict): 
    expires_at = 1992
    e = get_type_error_message(
        attr="expires_at", type_expected="datetime or None", got=expires_at
    )
    with pytest.raises(TypeError, match=e):
        ShortURL(**required_fields, expires_at=expires_at) # type: ignore


def test_last_accessed_at_invalid(required_fields: dict): 
    last_accessed_at = 1992
    e = get_type_error_message(
        attr="last_accessed_at",
        type_expected="datetime or None",
        got=last_accessed_at
    )
    with pytest.raises(TypeError, match=e):
        ShortURL(**required_fields, last_accessed_at=last_accessed_at) # type: ignore


def test_visist_count_lower_than_0(required_fields: dict):
    visit_count = -1
    e = ("The ShortURL visit_count must be greater than or equal to 0, "
        f"got {visit_count}")
    with pytest.raises(ValueError, match=e):
        ShortURL(**required_fields, visit_count=visit_count)
