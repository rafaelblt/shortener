import pytest

from shortener.domain.shorturl import ShortURL
from shortener.domain.shorturl.validators import CreateValidator
from shortener.domain.shorturl.exceptions import (
    ShortURLInvalidSlugError,
    ShortURLSlugAlreadyExistsError
)


@pytest.fixture
def validator(mock_shorturl_repository):
    return CreateValidator(repository=mock_shorturl_repository)


@pytest.mark.asyncio
async def test_check_slug_exists(
    validator: CreateValidator, normal_shorturl: ShortURL
):
    retrieved = await validator.check_slug_exists(normal_shorturl.slug)
    assert retrieved is None


@pytest.mark.asyncio
async def test_check_slug_exists_raises_slug_already_exists(
    validator: CreateValidator, normal_shorturl: ShortURL
):
    await validator.repository.save(normal_shorturl)
    with pytest.raises(
        ShortURLSlugAlreadyExistsError, 
        match="The provided slug already exists."
    ):
        await validator.check_slug_exists(normal_shorturl.slug)


@pytest.mark.asyncio
async def test_validate_slug(
    validator: CreateValidator, normal_shorturl: ShortURL
):    
    retrieved = await validator.validate_slug(normal_shorturl.slug)
    assert retrieved is None


@pytest.mark.asyncio
async def test_validate_slug_raises_slug_already_exists(
    validator: CreateValidator, normal_shorturl: ShortURL
):
    await validator.repository.save(normal_shorturl)
    with pytest.raises(ShortURLSlugAlreadyExistsError):
        await validator.validate_slug(normal_shorturl.slug)


@pytest.mark.asyncio
async def test_validate(
    validator: CreateValidator, normal_shorturl: ShortURL
):
    retrieved = await validator.validate(normal_shorturl)
    assert retrieved is None


@pytest.mark.asyncio
async def test_validate_raises_slug_already_exists(
    validator: CreateValidator, normal_shorturl: ShortURL
):
    await validator.repository.save(normal_shorturl)
    with pytest.raises(ShortURLSlugAlreadyExistsError):
        await validator.validate(normal_shorturl)
