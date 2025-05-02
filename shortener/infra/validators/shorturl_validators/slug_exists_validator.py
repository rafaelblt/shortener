from shortener.domain.shorturl import ShortURLRepository
from shortener.domain.shorturl.fields import Slug
from shortener.domain.shorturl.exceptions import ShortURLSlugAlreadyExistsError


async def validate_slug_exists(slug: Slug, repository: ShortURLRepository):
    if await repository.exists_by_slug(slug):
        raise ShortURLSlugAlreadyExistsError(provided_slug=slug)
