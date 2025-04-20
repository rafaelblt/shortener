from shortener.domain.shorturl import (
    ShortURL, ShortURLRepository, ShortURLValidator
)
from shortener.domain.shorturl.fields import URL, Slug


class PutShortURLUseCase:
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

    async def execute(self, id: int, slug: Slug, original_url: URL) -> ShortURL:
        """
        Executes the Use Case with the provided data.

        Args:
            id (int): The ShortURL id to be updated.
            slug (Slug): The updated slug.
            original_url (URL): The updated original_url.

        Returns:
            ShortURL: The ShortURL object updated.

        Raises:
            ShortURLValidationError: If any part of ShortURL is invalid.
        """
        shorturl = await self.repository.get_by_id(id)

        shorturl.slug = slug
        shorturl.original_url = original_url

        await self.validator.validate(shorturl)
        
        return await self.repository.update(shorturl)
