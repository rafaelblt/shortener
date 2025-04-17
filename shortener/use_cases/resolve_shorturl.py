from shortener.domain.shorturl import ShortURLRepository
from shortener.domain.shorturl.exceptions import ShortURLNotFoundInDatabaseError


class ResolveShortURLUseCase:
    """
    Use case to resolve a ShortURL object.
    """

    def __init__(self, repository: ShortURLRepository):
        """
        Initializes the use case with a repository.

        Args:
            repository (ShortURLRepository): The repository to get the ShortURL.
        """
        self.repository = repository
    
    async def resolve_slug(self, slug: str) -> str:
        """
        Get the original_url attr of a ShortURL in the repository with the slug.

        Args:
            slug (str): The ShortURL slug to be resolved.

        Returns:
            str: The original_url of ShortURL if is available.
        
        Raises:
            ShortURLNotFoundInDatabaseError: If the slug is not found in repository.
            ShortURLAvailabilityError: If the ShortURL status is different of ACTIVE.
        """
        shorturl = await self.repository.get_by_slug(slug)
    
        if shorturl is None:
            raise ShortURLNotFoundInDatabaseError()
        
        return shorturl.resolve()
