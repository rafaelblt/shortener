from shortener.domain.shorturl.shorturl import ShortURL
from shortener.domain.shorturl.repository import ShortURLRepository
from shortener.domain.shorturl.validator import ShortURLValidator

from .slug_exists_validator import validate_slug_exists


class ShortURLCreateValidator(ShortURLValidator):
    """ShortURL Validator class to validate a ShortURL to be created"""

    def __init__(self, repository: ShortURLRepository):
        self.repository = repository

    async def validate(self, shorturl: ShortURL):
        await validate_slug_exists(slug=shorturl.slug, repository=self.repository)
