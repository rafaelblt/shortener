import pytest
import pytest_asyncio

from sqlalchemy.orm.exc import UnmappedInstanceError

from shortener.domain.shorturl import ShortURL

from shortener.infra.db.models import ShortURLModel
from shortener.infra.db.repositories import SQLAlchemyShortURLRepository


@pytest_asyncio.fixture
async def repository(sqlalchemy_shorturl_repository):
    return sqlalchemy_shorturl_repository


def test_to_model(
    repository: SQLAlchemyShortURLRepository, normal_shorturl: ShortURL
):
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


def test_to_domain(
    repository: SQLAlchemyShortURLRepository, normal_shorturl: ShortURL
):
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


@pytest.mark.asyncio
async def test_save(
    repository: SQLAlchemyShortURLRepository, normal_shorturl: ShortURL
):
    retrieved = await repository.save(normal_shorturl)

    assert isinstance(retrieved, ShortURL)
    assert retrieved.id == 1
    assert retrieved.slug == normal_shorturl.slug

    saved_model = await repository.session.get(ShortURLModel, 1)
    assert saved_model.slug == normal_shorturl.slug


@pytest.mark.asyncio
async def test_get_all_with_no_shorturls(
    repository: SQLAlchemyShortURLRepository
):
    retrieved = await repository.get_all()

    assert isinstance(retrieved, list)
    assert len(retrieved) == 0


@pytest.mark.asyncio
async def test_get_all_with_shorturls(
    repository: SQLAlchemyShortURLRepository, 
    normal_shorturl: ShortURL,
    other_shorturl: ShortURL
):
    await repository.save(normal_shorturl)
    await repository.save(other_shorturl)

    retrieved = await repository.get_all()

    assert isinstance(retrieved, list)
    assert len(retrieved) == 2
    assert isinstance(retrieved[0], ShortURL)
    assert isinstance(retrieved[1], ShortURL)
    assert retrieved[0].id == 1
    assert retrieved[1].id == 2
    assert retrieved[0].slug == normal_shorturl.slug
    assert retrieved[1].slug == other_shorturl.slug


@pytest.mark.asyncio
async def test_get_by_id(
    repository: SQLAlchemyShortURLRepository, normal_shorturl: ShortURL
):
    await repository.save(normal_shorturl)

    retrieved = await repository.get_by_id(1)

    assert isinstance(retrieved, ShortURL)
    assert retrieved.id == 1
    assert retrieved.slug == normal_shorturl.slug


@pytest.mark.asyncio
async def test_get_by_slug(
    repository: SQLAlchemyShortURLRepository, normal_shorturl: ShortURL
):
    await repository.save(normal_shorturl)

    retrieved = await repository.get_by_slug(normal_shorturl.slug)

    assert isinstance(retrieved, ShortURL)
    assert retrieved.id == 1
    assert retrieved.original_url == normal_shorturl.original_url


@pytest.mark.asyncio
async def test_exists_by_slug(
    repository: SQLAlchemyShortURLRepository, normal_shorturl: ShortURL
):
    await repository.save(normal_shorturl)
    assert await repository.exists_by_slug(normal_shorturl.slug) is True


@pytest.mark.asyncio
async def test_exists_by_slug_false(
    repository: SQLAlchemyShortURLRepository, normal_shorturl: ShortURL
):
    assert await repository.exists_by_slug(normal_shorturl.slug) is False


@pytest.mark.asyncio
async def test_delete_by_id(
    repository: SQLAlchemyShortURLRepository, normal_shorturl: ShortURL
):
    await repository.save(normal_shorturl)

    retrieved = await repository.delete_by_id(1)

    assert isinstance(retrieved, ShortURL)
    assert retrieved.id == 1
    assert retrieved.slug == normal_shorturl.slug
    assert await repository.exists_by_slug(normal_shorturl.slug) is False


@pytest.mark.asyncio
async def test_delete_by_id_non_existent_shorturl(
    repository: SQLAlchemyShortURLRepository
):
    with pytest.raises(UnmappedInstanceError):
        await repository.delete_by_id(1)
