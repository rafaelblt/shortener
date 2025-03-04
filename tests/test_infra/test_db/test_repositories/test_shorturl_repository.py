from pytest import fixture, raises

from shortener.domain.shorturl import ShortURL
from shortener.domain.shorturl.exceptions import ShortURLDeletionNotFoundError

from shortener.infra.db.models import ShortURLModel
from shortener.infra.db.repositories import SQLAlchemyShortURLRepository


@fixture
def repository(sqlalchemy_shorturl_repository) -> SQLAlchemyShortURLRepository:
    repository = sqlalchemy_shorturl_repository
    return repository


@fixture
def repository_with_shorturl(
    repository: SQLAlchemyShortURLRepository, normal_shorturl: ShortURL
):
    repository.save(normal_shorturl)
    normal_shorturl.id = 1
    return (repository, normal_shorturl)


def test_method_get_by_id(repository_with_shorturl):
    repository = repository_with_shorturl[0]
    shorturl = repository_with_shorturl[1]

    retrieved = repository.get_by_id(shorturl.id)

    assert isinstance(retrieved, ShortURL)
    assert retrieved.id == shorturl.id


def test_method_get_by_slug(repository_with_shorturl):
    repository = repository_with_shorturl[0]
    shorturl = repository_with_shorturl[1]

    retrieved = repository.get_by_slug(shorturl.slug)

    assert isinstance(retrieved, ShortURL)
    assert retrieved.id == shorturl.id

def test_method_exists_by_slug(repository_with_shorturl):
    repository = repository_with_shorturl[0]
    shorturl = repository_with_shorturl[1]
    assert repository.exists_by_slug(shorturl.slug)


def test_method_exists_by_slug_false(repository, normal_shorturl):
    assert not repository.exists_by_slug(normal_shorturl.slug)


def test_method_save(repository, normal_shorturl):
    repository.save(normal_shorturl)
    saved_model = repository.session.get(ShortURLModel, 1)
    assert saved_model.slug == normal_shorturl.slug


def test_method_delete_by_id(repository_with_shorturl):
    repository = repository_with_shorturl[0]
    shorturl = repository_with_shorturl[1]

    retrieved = repository.delete_by_id(shorturl.id)

    assert isinstance(retrieved, ShortURL)
    assert retrieved.id == shorturl.id
    assert not repository.exists_by_slug(shorturl.slug)


def test_method_delete_by_id_raises_not_found_error(repository):
    example_id = 1
    with raises(
        ShortURLDeletionNotFoundError,
        match=f"ShortURL with id {example_id} not found for deletion."
    ):
        repository.delete_by_id(example_id)
    

def test_method_to_model(repository, normal_shorturl):
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


def test_method_to_domain(repository, normal_shorturl):
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
