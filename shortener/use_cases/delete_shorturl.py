from shortener.domain.shared.primarykey import PrimaryKey
from shortener.domain.shorturl import ShortURL, ShortURLRepository
from shortener.domain.shorturl.exceptions import ShortURLDeletionNotFoundError


class DeleteShortURLUseCase:
    """Use case to delete a ShortURL object from repository."""

    def __init__(self, repository: ShortURLRepository):
        """
        Initializes the use case with a repository.

        Args:
            repository (ShortURLRepository): The repository to delete ShortURL 
                objects.
        """
        self.repository = repository

    async def delete_by_pk(self, pk: PrimaryKey) -> ShortURL:
        """
        Deletes a ShortURL by its PrimaryKey.

        Args:
            pk (PrimaryKey): The primarykey of the ShortURL to delete.

        Returns:
            ShortURL: The ShortURL object that was deleted, or None if not found.

        Raises:
            ShortURLDeletionNotFoundError: If the ShortURL to be deleted is not 
                found.
        """
        shorturl = await self.repository.get_by_pk(pk)

        # TODO: future validations for deletion

        if shorturl:
            await self.repository.delete_by_pk(pk)
            return shorturl
        
        raise ShortURLDeletionNotFoundError(
            f"ShortURL with pk {pk} not found for deletion."
        )
