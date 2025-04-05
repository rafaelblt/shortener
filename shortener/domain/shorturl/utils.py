from shortener.domain.shorturl import ShortURLRepository
from shortener.domain.shorturl.slug import (
    Slug,
    DEFAULT_RANDOM_SLUG_LENGTH,
    DEFAULT_MAX_ATTEMPS_TO_GENERATE_UNIQUE_SLUG
)


async def generate_unique_slug( 
    repository: ShortURLRepository, 
    length: int = DEFAULT_RANDOM_SLUG_LENGTH,
    max_attempts: int = DEFAULT_MAX_ATTEMPS_TO_GENERATE_UNIQUE_SLUG
) -> Slug:
    """
    Generates a unique slug of a specified length.

    This function generates a random slug and checks its uniqueness against 
    the provided repository. If the slug already exists, it continues 
    generating new slugs until a unique one is found or until max_attempts 
    is reached.

    Args:
        repository (ShortURLRepository): The repository to check for 
            existing slugs.
        length (Optional[int]): The length of the slug to generate. 
        max_attempts (Optional[int]): The maximum number of attempts 
            to generate a unique slug.

    Returns:
        Slug: A unique slug.

    Raises:
        RuntimeError: If a unique slug cannot be found within max_attempts.
    """
    attempts = 0

    while attempts <= max_attempts:
        attempts += 1
        slug = Slug.generate_random(length=length)
        
        if not await repository.exists_by_slug(slug):
            return slug

    raise RuntimeError(
        f"Could not generate a unique slug after {max_attempts} attempts."
    )
