import pytest

from shortener.domain.shorturl import ShortURL


@pytest.fixture
def mock_repository(mock_shorturl_repository):
    return mock_shorturl_repository


def test_to_dict(mock_repository, normal_shorturl):
    shorturl_dict = mock_repository._to_dict(normal_shorturl)
    assert isinstance(shorturl_dict, dict)
    assert shorturl_dict["id"] == normal_shorturl.id
    assert shorturl_dict["slug"] == normal_shorturl.slug
    assert shorturl_dict["original_url"] == normal_shorturl.original_url
    assert shorturl_dict["owner_id"] == normal_shorturl.owner_id
    assert shorturl_dict["is_active"] == normal_shorturl.is_active
    assert shorturl_dict["visit_count"] == normal_shorturl.visit_count
    assert shorturl_dict["created_at"] == normal_shorturl.created_at
    assert shorturl_dict["expires_at"] == normal_shorturl.expires_at
    assert shorturl_dict["last_accessed_at"] == normal_shorturl.last_accessed_at


def test_to_domain(mock_repository, normal_shorturl):
    shorturl_dict = mock_repository._to_dict(normal_shorturl)
    domain = mock_repository._to_domain(shorturl_dict)
    assert domain.id == shorturl_dict["id"]
    assert domain.slug == shorturl_dict["slug"]
    assert domain.original_url == shorturl_dict["original_url"]
    assert domain.owner_id == shorturl_dict["owner_id"]
    assert domain.is_active == shorturl_dict["is_active"]
    assert domain.visit_count == shorturl_dict["visit_count"]
    assert domain.created_at == shorturl_dict["created_at"]
    assert domain.expires_at == shorturl_dict["expires_at"]
    assert domain.last_accessed_at == shorturl_dict["last_accessed_at"]


def test_save_shorturl(mock_repository, normal_shorturl):
    mock_repository.save(normal_shorturl)
    shorturl_dict = mock_repository.data[1]
    assert shorturl_dict["id"] == 1
    assert shorturl_dict["slug"] == normal_shorturl.slug


def test_get_by_id(mock_repository, normal_shorturl):
    mock_repository.save(normal_shorturl)
    mock_repository.get_by_id(1)

    retrieved = mock_repository.get_by_id(1)

    assert isinstance(retrieved, ShortURL)
    assert retrieved.id == 1
    assert retrieved.slug == normal_shorturl.slug


def test_get_by_slug(mock_repository, normal_shorturl):
    mock_repository.save(normal_shorturl)

    retrieved = mock_repository.get_by_slug(normal_shorturl.slug)

    assert isinstance(retrieved, ShortURL)
    assert retrieved.slug == normal_shorturl.slug


def test_exists_by_slug(mock_repository, normal_shorturl):
    mock_repository.save(normal_shorturl)
    assert mock_repository.exists_by_slug(normal_shorturl.slug) is True
    assert mock_repository.exists_by_slug("nonexistentslug") is False


def test_delete_by_id(mock_repository, normal_shorturl):
    mock_repository.save(normal_shorturl) 

    deleted = mock_repository.delete_by_id(1)

    assert isinstance(deleted, ShortURL)
    assert deleted.id == 1
    assert deleted.slug == normal_shorturl.slug
    assert mock_repository.get_by_id(1) is None
