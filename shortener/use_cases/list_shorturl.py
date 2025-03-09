from shortener.domain.shorturl import ShortURL, ShortURLRepository


class ListShortURLUseCase:
    """Use case to list ShortURLs objects from repository"""

    def __init__(self, repository: ShortURLRepository):
        """
        Initializes the use case with a repository.
        
        Args:
            repository (ShortURLRepository): The repository to get the ShortURLs.
        """
        self.repository = repository

    async def list_all(self) -> list[ShortURL]:
        """
        List all ShortURLs of the repository.

        Returns:
            list[ShortURL]: The list with ShortURLs.
        """
        return await self.repository.get_all()
