from abc import ABC, abstractmethod
from shortener.domain.shared import PaginatedResult
from shortener.domain.shorturl import ShortURL


class ShortURLRepository(ABC):

    @abstractmethod
    async def add(self, shorturl: ShortURL) -> ShortURL:
        """
        Add a ShortURL object to the database and return the updated object.

        Args:
            shorturl (ShortURL): The ShortURL domain object.
        
        Returns:
            ShortURL: Return the domain object updated.
        """

    @abstractmethod
    async def update(self, shorturl: ShortURL) -> ShortURL:
        """
        Update a existent ShortURL in database.

        Args:
            shorturl (ShortURL): The ShortURL domain object to update.
        
        Returns:
            ShortURL: The updated entity.
        
        Raises:
            ShortURLInvalidToUpdate: ShortURL without id.
            ShortURLNotFoundInDatabase: ShortURL not found in database.
        """

    @abstractmethod
    async def get_all(self) -> list[ShortURL]:
        pass

    @abstractmethod
    async def get_by_id(self, id: int) -> ShortURL | None:
        """
        Retrieves a ShortURL by its id.

        Args:
            id (int): The ShortURL id.

        Returns:
            Optional[ShortURL]: The entity object or None if not found.
        """
        pass

    @abstractmethod
    async def get_by_slug(self, slug: str) -> ShortURL | None:
        """
        Retrieves a ShortURL by its slug.

        Args:
            slug (str): The ShortURL slug.

        Returns:
            Optional[ShortURL]: The entity object or None if not found.
        """
        pass

    @abstractmethod
    async def list_paginated(self, offset: int, limit: int) -> PaginatedResult[ShortURL]:
        """
        Retrieve a paginated list of ShortURL objects.

        Args:
            offset (int): The starting index of the pagination.
            limit (int): The maximum number of items to retrieve.

        Returns:
            PaginatedResult[ShortURL]: A paginated result containing the objects. 
        """
        pass

    @abstractmethod
    async def delete_by_id(self, id: int) -> ShortURL:
        """
        Delete a existent ShortURL from the database.

        Args:
            id (int): The id of ShortURL to be deleted.
        
        Returns:
            ShortURL: The deleted entity.
        
        Raises:
            ShortURLNotFoundInDatabase: Id not found in database.
        """
        pass

    @abstractmethod
    async def exists_by_slug(self, slug: str) -> bool:
        """
        Check if a ShortURL with the given slug exists in the database.

        Args:
            slug (str): The slug to check.

        Returns:
            bool: True if a ShortURL with the given slug exists, False otherwise.
        """
        pass
