from pytest import fixture

from shortener.infrastructure.db.models import ShortURLModel


@fixture
def repository(sqlalchemy_shorturl_repository):
    repository = sqlalchemy_shorturl_repository
    return repository


@fixture
def repository_with_shorturl(repository, normal_shorturl):
    repository.save(normal_shorturl)
    return repository


def test_method_save(repository, normal_shorturl):
    repository.save(normal_shorturl)

    retrieved = repository.session.query(ShortURLModel).filter_by(
        slug=normal_shorturl.slug
    ).one()

    assert retrieved.id is not None
    assert retrieved.slug == normal_shorturl.slug
    assert retrieved.original_url == normal_shorturl.original_url


def test_method_get_by_slug(repository_with_shorturl, normal_shorturl):
    retrieved = repository_with_shorturl.get_by_slug(normal_shorturl.slug)

    assert retrieved.id is not None
    assert retrieved.slug == normal_shorturl.slug
    assert retrieved.original_url == normal_shorturl.original_url


def test_exists_by_slug(repository_with_shorturl, normal_shorturl):
    assert repository_with_shorturl.exists_by_slug(normal_shorturl.slug)


def test_not_exists_by_slug(repository, normal_shorturl):
    assert not repository.exists_by_slug(normal_shorturl.slug)


def test_to_model(repository, normal_shorturl):
    model = repository._to_model(normal_shorturl)

    assert model.id == normal_shorturl.id
    assert model.slug == normal_shorturl.slug
    assert model.original_url == normal_shorturl.original_url
    assert model.is_active == normal_shorturl.is_active
    assert model.visit_count == normal_shorturl.visit_count
    assert model.created_at == normal_shorturl.created_at
    assert model.expires_at == normal_shorturl.expires_at
    assert model.last_accessed_at == normal_shorturl.last_accessed_at


def test_to_domain(repository, normal_shorturl):
    model = repository._to_model(normal_shorturl)
    domain = repository._to_domain(model)

    assert domain.id == model.id
    assert domain.slug == model.slug
    assert domain.original_url == model.original_url
    assert domain.is_active == model.is_active
    assert domain.visit_count == model.visit_count
    assert domain.created_at == model.created_at
    assert domain.expires_at == model.expires_at
    assert domain.last_accessed_at == model.last_accessed_at
