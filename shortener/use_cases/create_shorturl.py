from typing import Optional

from shortener.domain.shorturl import (
    ShortURL,
    ShortURLRepository,
    ShortURLValidator,
)
from shortener.domain.shorturl.fields import Slug, URL
from shortener.domain.shorturl.utils import generate_unique_slug
from shortener.domain.user import User


class CreateShortURLUseCase:
    """Use case to create a new ShortURL object and save in repository."""

    def __init__(
        self, 
        repository: ShortURLRepository,
        validator: ShortURLValidator,
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
        original_url: URL,
        custom_slug: Optional[Slug] = None,
        owner: Optional[User] = None
    ) -> ShortURL:
        """
        Executes the Use Case with the provided data.

        Args:
            original_url (URL): The original_url to be shortened.
            custom_slug (Optional[Slug]): Custom slug of the ShortURL. Will be 
                generated if not provided.
            owner (Optional[User]): Onwer of the ShortURL. Defaults to None.

        Returns:
            ShortURL: The entity object created.

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
            owner=owner,
        )

        await self.validator.validate(shorturl)
        
        return await self.repository.add(shorturl)
