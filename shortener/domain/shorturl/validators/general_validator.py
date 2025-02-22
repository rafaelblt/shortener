from shortener.domain.shorturl.repository import ShortURLRepository
from shortener.domain.shorturl.rules import is_slug_forbidden
from shortener.domain.shorturl import ShortURL

from shortener.domain.shorturl.exceptions import *

from .base import ShortURLValidator


class GeneralShortURLValidator(ShortURLValidator):
    
    def __init__(self, repository: ShortURLRepository):
        self.repository = repository

    def validate(self, shorturl: ShortURL):

        self._validate_slug(shorturl.slug)

    def _validate_slug(self, slug: str) -> None:
        if self.repository.exists_by_slug(slug):
            raise SlugAlreadyExistsException()

        if is_slug_forbidden(slug):
            raise InvalidSlugException()
