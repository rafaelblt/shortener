import pytest
import pytest_asyncio

from shortener.domain.shorturl import ShortURL
from shortener.domain.shorturl.exceptions import ShortURLDeletionNotFoundError

from shortener.use_cases import DeleteShortURLUseCase


@pytest_asyncio.fixture
async def use_case(mock_shorturl_repository, normal_shorturl):
    await mock_shorturl_repository.save(normal_shorturl)
    return DeleteShortURLUseCase(repository=mock_shorturl_repository)


@pytest.mark.asyncio
async def test_delete_by_id(
    use_case: DeleteShortURLUseCase, normal_shorturl: ShortURL
):
    normal_shorturl.id = 1
    retrieved = await use_case.delete_by_id(normal_shorturl.id)
    assert retrieved.id == normal_shorturl.id
    assert retrieved.slug == normal_shorturl.slug


@pytest.mark.asyncio
async def test_raises_not_found_delete_by_id(use_case: DeleteShortURLUseCase):
    example_id = 2
    with pytest.raises(
        ShortURLDeletionNotFoundError,
        match=f"ShortURL with id {example_id} not found for deletion."
    ):
        await use_case.delete_by_id(example_id)
