import pytest

from shortener.domain.shared.primarykey import PrimaryKey
from tests.utils.entity_helpers import assert_shorturl_fields

from shortener.domain.shorturl import ShortURL, ShortURLValidator
from shortener.domain.shorturl.fields import Slug, URL
from shortener.domain.shorturl.exceptions import ShortURLValidationError

from shortener.use_cases.update_shorturl import UpdateShortURLUseCase


class MockValidator(ShortURLValidator):
    async def validate(self, shorturl: ShortURL):
        if shorturl.slug == "joker-joker-joker":
            raise ShortURLValidationError()

@pytest.fixture
def use_case(mock_shorturl_repository):
    return UpdateShortURLUseCase(
        repository=mock_shorturl_repository,
        validator=MockValidator()
    )


@pytest.mark.asyncio
async def test_with_non_existent_shorturl(use_case: UpdateShortURLUseCase):
    pk = PrimaryKey.create_pk_id(1)
    with pytest.raises(
        ShortURLValidationError,
        match=f"There is no shorturl in the database with the given pk: {pk}"
    ):
        await use_case.execute(
            pk=pk, slug=Slug("test"), original_url=URL("https://test.com")
        )


@pytest.mark.asyncio
async def test_instance_retrieved(
    use_case: UpdateShortURLUseCase, normal_shorturl: ShortURL
):
    shorturl = await use_case.repository.add(normal_shorturl)
    
    new_slug = Slug("test-updated-slug")
    new_url = URL("https://newurl.com")

    retrieved = await use_case.execute(
        pk=shorturl.pk,
        slug=new_slug,
        original_url=new_url
    )

    assert isinstance(retrieved, ShortURL)
    assert retrieved.pk.get_id() == 1

    normal_shorturl.change_slug(new_slug)
    normal_shorturl.change_original_url(new_url)

    assert_shorturl_fields(retrieved, normal_shorturl, ignore_pk=True)
    

@pytest.mark.asyncio
async def test_raises_validation_error(
    use_case: UpdateShortURLUseCase, normal_shorturl: ShortURL
):
    shorturl = await use_case.repository.add(normal_shorturl)
    new_slug = Slug("joker-joker-joker")

    with pytest.raises(ShortURLValidationError):
        await use_case.execute(pk=shorturl.pk, slug=new_slug)


@pytest.mark.asyncio
async def test_if_shorturl_is_updated_in_repository(
    use_case: UpdateShortURLUseCase, normal_shorturl: ShortURL
):
    shorturl = await use_case.repository.add(normal_shorturl)
    new_slug = Slug("test-updated-slug")

    await use_case.execute(pk=shorturl.pk, slug=new_slug)

    assert await use_case.repository.exists_by_slug(new_slug)
