from typing import Optional

from shortener.domain.shorturl import ShortURL, ShortURLRepository
from shortener.domain.shorturl.exceptions import ShortURLSlugAlreadyExistsError
from shortener.domain.shorturl.fields import Slug, URL
from shortener.domain.shorturl.utils import generate_unique_slug
from shortener.domain.user.exceptions import UserNotFoundError


class CreateShortURLUseCase:
    """Use case to create a new ShortURL object."""

    def __init__(
        self, 
        shorturl_repository: ShortURLRepository,
    ):
        self.shorturl_repository = shorturl_repository

    async def execute(
        self, 
        original_url: URL,
        custom_slug: Optional[Slug] = None,
    ) -> ShortURL:
        """
        Executes the Use Case with the provided data.

        Args:
            original_url (URL): The original_url to be shortened.
            custom_slug (Optional[Slug]): Custom slug of the ShortURL. Will be 
                generated if not provided.

        Returns:
            ShortURL: The entity object created.

        Raises:
            ShortURLSlugAlreadyExistsError: If the given custom_slug already 
                exists.
        """
        if custom_slug and await self.shorturl_repository.exists_by_slug(custom_slug):
            raise ShortURLSlugAlreadyExistsError(custom_slug)

        slug = custom_slug or await generate_unique_slug(self.shorturl_repository)

        shorturl = ShortURL(
            slug=slug,
            original_url=original_url,
        )
        shorturl = await self.shorturl_repository.add(shorturl)
        
        return shorturl
