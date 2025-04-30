from typing import Optional

from shortener.domain.user import User, UserRepository

from shortener.domain.shorturl import (
    ShortURL,
    ShortURLRepository,
    ShortURLValidator,
)
from shortener.domain.shorturl.fields import Slug, URL
from shortener.domain.shorturl.utils import generate_unique_slug
from shortener.domain.shorturl.exceptions import ShortURLValidationError


class CreateShortURLUseCase:
    """Use case to create a new ShortURL object."""

    def __init__(
        self, 
        shorturl_repository: ShortURLRepository,
        user_repository: UserRepository,
        validator: ShortURLValidator,
    ):
        """
        Args:
            shorturl_repository (ShortURLRepository): Repository to save the 
                ShortURL object.
            user_repository (UserRepository): Repository to get the ShortURL owner.
            validator (ShortURLValidator): Validator to validate the ShortURL data.
        """
        self.shorturl_repository = shorturl_repository
        self.user_repository = user_repository
        self.validator = validator

    async def execute(
        self, 
        original_url: URL,
        owner_id: int,
        custom_slug: Optional[Slug] = None,
    ) -> ShortURL:
        """
        Executes the Use Case with the provided data.

        Args:
            original_url (URL): The original_url to be shortened.
            owner_id (int): Owner ID of the ShortURL.
            custom_slug (Optional[Slug]): Custom slug of the ShortURL. Will be 
                generated if not provided.

        Returns:
            ShortURL: The entity object created.

        Raises:
            ShortURLValidationError: If any part of ShortURL is invalid.
        """
        owner = await self.user_repository.get_by_id(owner_id)
        if owner is None:
            raise ShortURLValidationError(
                "There is no user in the database with the given owner_id."
            )

        slug = custom_slug or await generate_unique_slug(self.shorturl_repository)

        shorturl = ShortURL(
            slug=slug,
            original_url=original_url,
            owner=owner,
        )

        await self.validator.validate(shorturl)
        
        return await self.shorturl_repository.add(shorturl)
