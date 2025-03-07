from shortener.domain.shorturl import ShortURL, ShortURLRepository


class GetShortURLUseCase:
    """Use case to get a ShortURL object from repository."""

    def __init__(self, repository: ShortURLRepository):
        """
        Initializes the use case with a repository.

        Args:
            repository (ShortURLRepository): The repository to get  ShortURL 
                objects.
        """
        self.repository = repository

    async def get_by_id(self, id: int) -> ShortURL | None:
        """
        Get a ShortURL by its ID.

        Args:
            id (int): The ID of the ShortURL.

        Returns:
            Optional[ShortURL]: The ShortURL object or None if not found.
        """
        return await self.repository.get_by_id(id)
    
    async def get_by_slug(self, slug: str) -> ShortURL | None:
        """
        Get a ShortURL by its slug.

        Args:
            slug (str): The slug of the ShortURL.

        Returns:
            Optional[ShortURL]: The ShortURL object or None if not found.
        """
        return await self.repository.get_by_slug(slug)
