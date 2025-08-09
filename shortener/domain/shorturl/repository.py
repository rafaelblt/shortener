from abc import ABC, abstractmethod

from shortener.domain.shared.primarykey import PrimaryKey
from shortener.domain.shared.pagination import PaginatedResult

from shortener.domain.shorturl import ShortURL
from shortener.domain.shorturl.exceptions import ShortURLNotFoundError


class ShortURLRepository(ABC):
    EntityType = ShortURL
    exceptions = {
        "entity_not_found": ShortURLNotFoundError
    }

    @abstractmethod
    async def add(self, shorturl: ShortURL) -> ShortURL:
        """
        Add a ShortURL object to the database and return the updated object.

        Args:
            shorturl (ShortURL): The object to add.
        
        Returns:
            ShortURL: Return the added object.
        """

    @abstractmethod
    async def update(self, shorturl: ShortURL) -> ShortURL:
        """
        Update a existent ShortURL in database.

        Args:
            shorturl (ShortURL): The object to update.
        
        Returns:
            ShortURL: The updated entity.
        
        Raises:
            ShortURLInvalidToUpdateError: ShortURL without id.
            ShortURLNotFoundError: ShortURL not found in database.
        """
        pass

    @abstractmethod
    async def get_all(self) -> list[ShortURL]:
        """
        Retrieve all ShortURL objects from the database.

        Returns:
            list[ShortURL]: A list of all ShortURL objects.
        """
        pass

    @abstractmethod
    async def get_by_pk(self, pk: PrimaryKey) -> ShortURL | None:
        """
        Retrieves a ShortURL by its pk.

        Args:
            pk (PrimaryKey): The ShortURL pk.

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
    async def delete_by_pk(self, pk: PrimaryKey) -> ShortURL:
        """
        Delete a existent ShortURL from the database.

        Args:
            pk (PrimaryKey): The pk of ShortURL to be deleted.
        
        Returns:
            ShortURL: The deleted entity.
        
        Raises:
            ShortURLNotFoundError: ShortURL not found in database.
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
