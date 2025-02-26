from shortener.domain.shorturl import ShortURL
from shortener.domain.shorturl.repository import ShortURLRepository
from shortener.domain.shorturl.rules import (
    is_slug_forbidden, 
    is_slug_shorter_than_min_length, 
    is_slug_longer_than_max_length
)

from shortener.domain.shorturl.exceptions import (
    ShortURLSlugAlreadyExistsError, 
    ShortURLForbiddenSlugError,
    ShortURLSlugTooLongError,
    ShortURLSlugTooShortError
)

from .base_validator import ShortURLValidator


class GeneralValidator(ShortURLValidator):
    """ShortURL Validator class to validate all entity fields."""
    
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
        """
        Args: 
            slug (str): The slug to be validated.

        Returns:
            None: The slug is valid.

        Raises:
            ShortURLSlugAlreadyExistsError: The slug already exists in repository.
            ShortURLForbiddenSlugError: The slug is forbidden.
            ShortURLSlugTooLongError: The slug is longer than max length.
            ShortURLSlugTooShortError: The slug is shorther than min length.
        """
        if is_slug_forbidden(slug):
            raise ShortURLForbiddenSlugError(
                "The provided slug is forbidden."
            )
        
        if is_slug_longer_than_max_length(slug):
            raise ShortURLSlugTooLongError(
                "The provided slug is longer than max length"
            )
        
        if is_slug_shorter_than_min_length(slug):
            raise ShortURLSlugTooShortError(
                "The provided slug is shorter than min length"
            )
        
        if self.repository.exists_by_slug(slug):
            raise ShortURLSlugAlreadyExistsError(
                "The provided slug already exists."
            )
