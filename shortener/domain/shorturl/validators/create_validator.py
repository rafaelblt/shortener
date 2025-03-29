from shortener.domain.shorturl import ShortURL, Slug, URL, ShortURLRepository
from shortener.domain.shorturl.exceptions import (
    ShortURLSlugAlreadyExistsError,
    ShortURLInvalidSlugError
)


class CreateValidator:
    """ShortURL Validator class to validate a ShortURL to be created"""

    def __init__(self, repository: ShortURLRepository):
        """
        Args:
            repository (ShortURLRepository): Use to validate if slug already
                exists
        """
        self.repository = repository

    async def validate(self, shorturl: ShortURL):
        await self._validate_slug(shorturl.slug)
        await self._validate_original_url(shorturl.original_url)

    async def _validate_slug(self, slug: Slug):
        await self._check_slug_exists(slug)
        
    async def _check_slug_exists(self, slug: Slug):
        if await self.repository.exists_by_slug(slug):
            raise ShortURLSlugAlreadyExistsError(
                "The provided slug already exists."
            )
        
    async def _validate_original_url(self, url: URL):
        pass