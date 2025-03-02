from shortener.domain.shorturl import ShortURL, ShortURLRepository
from shortener.domain.shorturl.exceptions import ShortURLDeletionNotFoundError


class DeleteShortURLUseCase:
    """Use case to delete a ShortURL object"""

    def __init__(self, repository: ShortURLRepository):
        """
        Initializes the use case with a repository.

        Args:
            repository (ShortURLRepository): The repository to delete ShortURL 
                objects.
        """
        self.repository = repository

    def delete_by_id(self, id: int) -> ShortURL:
        """
        Deletes a ShortURL by its ID.

        Args:
            id (int): The ID of the ShortURL to delete.

        Returns:
            ShortURL: The ShortURL object that was deleted, or None if not found.

        Raises:
            ShortURLDeletionNotFoundError: If the ShortURL to be deleted is not 
                found.
        """
        shorturl = self.repository.get_by_id(id)

        # TODO: future validations for deletion

        if shorturl:
            self.repository.delete_by_id(id)
            return shorturl
        
        raise ShortURLDeletionNotFoundError(
            f"ShortURL with id {id} not found for deletion."
        )
