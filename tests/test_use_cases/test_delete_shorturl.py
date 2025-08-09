import pytest
import pytest_asyncio

from shortener.domain.shared.primarykey import PrimaryKey
from shortener.domain.shorturl import ShortURL
from shortener.domain.shorturl.exceptions import ShortURLDeletionNotFoundError

from shortener.use_cases import DeleteShortURLUseCase


@pytest_asyncio.fixture
async def use_case(mock_shorturl_repository):
    return DeleteShortURLUseCase(repository=mock_shorturl_repository)


@pytest.mark.asyncio
async def test_delete_by_pk(
    use_case: DeleteShortURLUseCase, normal_shorturl: ShortURL
):
    shorturl = await use_case.repository.add(normal_shorturl)
    retrieved = await use_case.delete_by_pk(shorturl.pk)

    assert retrieved.pk == shorturl.pk
    assert retrieved.slug == shorturl.slug


@pytest.mark.asyncio
async def test_delete_by_pk_raises_not_found(use_case: DeleteShortURLUseCase):
    example_pk = PrimaryKey.create_pk_id(1)
    with pytest.raises(
        ShortURLDeletionNotFoundError,
        match=f"ShortURL with pk {example_pk} not found for deletion."
    ):
        await use_case.delete_by_pk(example_pk)
