from typing import Optional

from shortener.domain.shared.primarykey import PrimaryKey
from shortener.domain.shorturl import (
    ShortURL, ShortURLRepository, ShortURLValidator
)
from shortener.domain.shorturl.exceptions import ShortURLValidationError
from shortener.domain.shorturl.fields import URL, Slug


class UpdateShortURLUseCase:
    """Use case to update a ShortURL object."""

    def __init__(
            self, 
            repository: ShortURLRepository,
            validator: ShortURLValidator
        ):
        """
        Args:
            repository (ShortURLRepository): Repository to save the ShortURL object.
            validator (ShortURLValidator): Validator to validate the ShortURL data.
        """
        self.repository = repository
        self.validator = validator

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
            ShortURLValidationError: If any part of ShortURL is invalid.
        """
        shorturl = await self.repository.get_by_pk(pk)
        if shorturl is None:
            raise ShortURLValidationError(
                f"There is no shorturl in the database with the given pk: {pk}"
            )
        
        new_slug = slug or shorturl.slug
        new_original_url = original_url or shorturl.original_url
        shorturl.change_slug(new_slug)        
        shorturl.change_original_url(new_original_url)

        await self.validator.validate(shorturl)

        return await self.repository.update(shorturl)
