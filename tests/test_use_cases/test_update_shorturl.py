import pytest

from shortener.domain.shared.exceptions import MultiValidationError, ValidationError
from shortener.domain.shared.primarykey import PrimaryKey
from shortener.domain.shared.validator import Validator

from shortener.domain.shorturl import ShortURL
from shortener.domain.shorturl.fields import Slug, URL
from shortener.domain.shorturl.exceptions import ShortURLNotFoundError

from shortener.use_cases.update_shorturl import UpdateShortURLUseCase

from tests.utils.entity_helpers import assert_shorturl_fields


class MockSlugValidator(Validator):
    async def validate(self, value: str):
        if value == "joker-joker-joker":
            raise ValidationError(value, "slug", "SLUG_ERROR", "error message")


class MockOriginalURLValidator(Validator):
    async def validate(self, value: str):
        if value == "https://joker.com":
            raise ValidationError(value, "original_url", "URL_ERROR", "error message")


@pytest.fixture
def use_case(mock_shorturl_repository):
    return UpdateShortURLUseCase(
        shorturl_repository=mock_shorturl_repository,
        validators_map={
            "slug": [MockSlugValidator()],
            "original_url": [MockOriginalURLValidator()]
        }
    )


@pytest.mark.asyncio
async def test_raises_slug_validation_error(
    use_case: UpdateShortURLUseCase, normal_shorturl: ShortURL
):
    shorturl = await use_case.shorturl_repository.add(normal_shorturl)
    new_slug = Slug("joker-joker-joker")

    with pytest.raises(MultiValidationError) as error:
        await use_case.execute(pk=shorturl.pk, slug=new_slug)
    assert error.value.errors[0].code == "SLUG_ERROR"


@pytest.mark.asyncio
async def test_raises_original_url_validation_error(
    use_case: UpdateShortURLUseCase, normal_shorturl: ShortURL
):
    shorturl = await use_case.shorturl_repository.add(normal_shorturl)
    new_url = URL("https://joker.com")

    with pytest.raises(MultiValidationError) as error:
        await use_case.execute(pk=shorturl.pk, original_url=new_url)
    assert error.value.errors[0].code == "URL_ERROR"


@pytest.mark.asyncio
async def test_with_non_existent_shorturl(use_case: UpdateShortURLUseCase):
    pk = PrimaryKey.create_pk_id(1)
    with pytest.raises(ShortURLNotFoundError) as error:
        await use_case.execute(
            pk=pk, slug=Slug("test"), original_url=URL("https://test.com")
        )
    assert error.value.value == pk
    assert error.value.field == "pk"


@pytest.mark.asyncio
async def test_instance_retrieved(
    use_case: UpdateShortURLUseCase, normal_shorturl: ShortURL
):
    shorturl = await use_case.shorturl_repository.add(normal_shorturl)
    
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
async def test_if_shorturl_is_updated_in_repository(
    use_case: UpdateShortURLUseCase, normal_shorturl: ShortURL
):
    shorturl = await use_case.shorturl_repository.add(normal_shorturl)
    new_slug = Slug("test-updated-slug")

    await use_case.execute(pk=shorturl.pk, slug=new_slug)

    assert await use_case.shorturl_repository.exists_by_slug(new_slug)
