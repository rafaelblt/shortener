from shortener.domain.shorturl.shorturl import ShortURL
from shortener.domain.shorturl.repository import ShortURLRepository
from shortener.domain.shorturl.validator import ShortURLValidator
from shortener.domain.shorturl.exceptions import (
    ShortURLSlugAlreadyExistsError
)


class ShortURLCreateValidator(ShortURLValidator):
    """ShortURL Validator class to validate a ShortURL to be created"""

    def __init__(self, repository: ShortURLRepository):
        self.repository = repository

    async def validate(self, shorturl: ShortURL):
        if await self.repository.exists_by_slug(shorturl.slug):
            raise ShortURLSlugAlreadyExistsError(provided_slug=shorturl.slug)
