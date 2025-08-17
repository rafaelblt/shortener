from typing import Optional

from shortener.domain.shared.primarykey import PrimaryKey
from shortener.domain.shared.validator import MultiFieldValidator

from shortener.domain.shorturl import ShortURL, ShortURLRepository
from shortener.domain.shorturl.exceptions import ShortURLNotFoundError, ShortURLSlugAlreadyExistsError
from shortener.domain.shorturl.fields import URL, Slug

from .types import ValidatorsMapType


class UpdateShortURLUseCase:
    """Use case to update a ShortURL object."""

    def __init__(
            self, 
            shorturl_repository: ShortURLRepository,
            validators_map: ValidatorsMapType
        ):
        """
        Args:
            shorturl_repository (ShortURLRepository): Repository to save the ShortURL object.
        """
        self.shorturl_repository = shorturl_repository
        self.validators_map = validators_map

    async def execute(
        self,
        pk: PrimaryKey,
        slug: Optional[Slug] = None,
        original_url: Optional[URL] = None
    ) -> ShortURL:
        """
        Executes the Use Case with the provided data.

        Args:
            pk (PrimaryKey): The ShortURL pk to be updated.
            slug (Optional[Slug]): The updated slug.
            original_url (Optional[URL)]: The updated original_url.

        Returns:
            ShortURL: The ShortURL object updated.

        Raises:
            ShortURLNotFoundError: If shorturl with the given pk does not exist.
        """
        multi_validator = MultiFieldValidator(self.validators_map)
        await multi_validator.validate(slug=slug, original_url=original_url)

        if slug and await self.shorturl_repository.exists_by_slug(slug):
            raise ShortURLSlugAlreadyExistsError(slug)

        shorturl = await self.shorturl_repository.get_by_pk(pk)
        if shorturl is None:
            raise ShortURLNotFoundError(field="pk", value=pk)
        
        new_slug = slug or shorturl.slug
        new_original_url = original_url or shorturl.original_url
        shorturl.change_slug(new_slug)        
        shorturl.change_original_url(new_original_url)

        return await self.shorturl_repository.update(shorturl)
