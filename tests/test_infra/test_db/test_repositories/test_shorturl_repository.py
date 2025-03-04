from pytest import fixture, raises

from sqlalchemy.orm.exc import UnmappedInstanceError

from shortener.domain.shorturl import ShortURL

from shortener.infra.db.models import ShortURLModel
from shortener.infra.db.repositories import SQLAlchemyShortURLRepository


@fixture
def repository(sqlalchemy_shorturl_repository) -> SQLAlchemyShortURLRepository:
    return sqlalchemy_shorturl_repository


def test_to_model(repository, normal_shorturl):
    model = repository._to_model(normal_shorturl)

    assert isinstance(model, ShortURLModel)
    assert model.id == normal_shorturl.id
    assert model.slug == normal_shorturl.slug
    assert model.original_url == normal_shorturl.original_url
    assert model.is_active == normal_shorturl.is_active
    assert model.visit_count == normal_shorturl.visit_count
    assert model.created_at == normal_shorturl.created_at
    assert model.expires_at == normal_shorturl.expires_at
    assert model.last_accessed_at == normal_shorturl.last_accessed_at
    # TODO: assert owner attr when user entity and model are created


def test_to_domain(repository, normal_shorturl):
    model = repository._to_model(normal_shorturl)
    domain = repository._to_domain(model)

    assert isinstance(domain, ShortURL)
    assert domain.id == model.id
    assert domain.slug == model.slug
    assert domain.original_url == model.original_url
    assert domain.is_active == model.is_active
    assert domain.visit_count == model.visit_count
    assert domain.created_at == model.created_at
    assert domain.expires_at == model.expires_at
    assert domain.last_accessed_at == model.last_accessed_at
    # TODO: assert owner attr when user entity and model are created


def test_save(repository, normal_shorturl):
    retrieved = repository.save(normal_shorturl)

    assert isinstance(retrieved, ShortURL)
    assert retrieved.id == 1
    assert retrieved.slug == normal_shorturl.slug

    saved_model = repository.session.get(ShortURLModel, 1)
    
    assert saved_model.slug == normal_shorturl.slug


def test_get_by_id(repository, normal_shorturl):
    repository.save(normal_shorturl)

    retrieved = repository.get_by_id(1)

    assert isinstance(retrieved, ShortURL)
    assert retrieved.id == 1
    assert retrieved.slug == normal_shorturl.slug


def test_get_by_slug(repository, normal_shorturl):
    repository.save(normal_shorturl)

    retrieved = repository.get_by_slug(normal_shorturl.slug)

    assert isinstance(retrieved, ShortURL)
    assert retrieved.id == 1
    assert retrieved.original_url == normal_shorturl.original_url


def test_exists_by_slug(repository, normal_shorturl):
    repository.save(normal_shorturl)
    assert repository.exists_by_slug(normal_shorturl.slug) is True


def test_exists_by_slug_false(repository, normal_shorturl):
    assert repository.exists_by_slug(normal_shorturl.slug) is False


def test_delete_by_id(repository, normal_shorturl):
    repository.save(normal_shorturl)

    retrieved = repository.delete_by_id(1)

    assert isinstance(retrieved, ShortURL)
    assert retrieved.id == 1
    assert retrieved.slug == normal_shorturl.slug
    assert repository.exists_by_slug(normal_shorturl.slug) is False


def test_delete_by_id_non_existent_shorturl(repository):
    with raises(UnmappedInstanceError):
        repository.delete_by_id(1)
