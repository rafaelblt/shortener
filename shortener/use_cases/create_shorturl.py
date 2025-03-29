from typing import Optional
from datetime import datetime

from shortener.domain.shorturl import (
    ShortURL,
    URL,
    Slug,
    ShortURLRepository,
    ShortURLValidator,
)
from shortener.domain.shorturl.utils import generate_unique_slug


class CreateShortURLUseCase:
    """Use case to create a new ShortURL object and save in repository."""

    def __init__(
            self, 
            repository: ShortURLRepository,
            validator: ShortURLValidator,
        ):
        """
        Initializes the use case with a repository, validatior and slug generator.

        Args:
            repository (ShortURLRepository): Repository to save the ShortURL object.
            validator (ShortURLValidator): Validator to validate the ShortURL data.
        """
        self.repository = repository
        self.validator = validator

    async def execute(
        self, 
        original_url: URL,
        custom_slug: Optional[Slug] = None,
        owner_id: Optional[int] = None,
        expires_at: Optional[datetime] = None
    ) -> ShortURL:
        """
        Executes the Use Case with the provided data.

        Args:
            original_url (URL): The original_url to be shortened.
            custom_slug (Optional[Slug]): Custom slug of the ShortURL.
            owner_id (Optional[int]): User ID who created the ShortURL.
            expires_at (Optional[datetime]): Expiration date of the ShortURL.

        Returns:
            ShortURL: The ShortURL object.

        Raises:
            ShortURLValidationError: If any part of ShortURL is invalid.
        """
        if custom_slug is None:
            slug = await generate_unique_slug(repository=self.repository)
        else:
            slug = custom_slug

        shorturl = ShortURL(
            slug=slug,
            original_url=original_url,
            owner_id=owner_id,
            expires_at=expires_at
        )

        await self.validator.validate(shorturl)
        
        return await self.repository.save(shorturl)
