from shortener.domain.shorturl import ShortURL, Slug, ShortURLRepository
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

    async def _validate_slug(self, slug: Slug):
        if not isinstance(slug, Slug):
            raise ShortURLInvalidSlugError(
                "The slug attribute of the ShortURL is not a Slug instance"
            )
        await self._check_slug_exists(slug)
        
    async def _check_slug_exists(self, slug: Slug):
        if await self.repository.exists_by_slug(slug):
            raise ShortURLSlugAlreadyExistsError(
                "The provided slug already exists."
            )
