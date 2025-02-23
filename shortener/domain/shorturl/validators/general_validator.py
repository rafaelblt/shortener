from shortener.domain.shorturl.repository import ShortURLRepository
from shortener.domain.shorturl.rules import is_slug_forbidden
from shortener.domain.shorturl import ShortURL

from shortener.domain.shorturl.exceptions import (
    SlugAlreadyExistsException, InvalidSlugException
)

from .base_validator import ShortURLValidator


class GeneralShortURLValidator(ShortURLValidator):
    """Validator class for ShortURLs. It validate all entity fields."""
    
    def __init__(self, repository: ShortURLRepository):
        """
        Args:
            repository (ShortURLRepository): Use to validate if slug already
                exists
        """
        self.repository = repository

    def validate(self, shorturl: ShortURL) -> None:
        self._validate_slug(shorturl.slug)

    def _validate_slug(self, slug: str) -> None:
        if self.repository.exists_by_slug(slug):
            raise SlugAlreadyExistsException()

        if is_slug_forbidden(slug):
            raise InvalidSlugException()
