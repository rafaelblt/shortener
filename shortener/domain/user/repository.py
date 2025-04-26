from abc import ABC, abstractmethod

from shortener.domain.shared import PaginatedResult
from shortener.domain.user import User


class UserRepository(ABC):

    @abstractmethod
    async def add(self, user: User) -> User:
        """
        Add a User object to the database and return the updated object.

        Args:
            user (User): The object to add.
        
        Returns:
            User: Return the added object.
        """
        pass

    @abstractmethod
    async def update(self, user: User) -> User:
        """
        Update a existent User in database.

        Args:
            user (User): The object to update.
        
        Returns:
            User: The updated entity.
        
        Raises:
            UserInvalidToUpdate: User without id.
            UserNotFoundInDatabase: User not found in database.
        """
        pass

    @abstractmethod
    async def get_all(self) -> list[User]:
        """
        Retrieve all User objects from the database.

        Returns:
            list[User]: A list of all User objects.
        """
        pass

    @abstractmethod
    async def get_by_id(self, id: int) -> User | None:
        """
        Retrieves a User by its id.

        Args:
            id (int): The User id.

        Returns:
            Optional[User]: The entity object or None if not found.
        """
        pass

    @abstractmethod
    async def get_by_email(self, email: str) -> User | None:
        """
        Retrieves a User by its email.

        Args:
            email (str): The User email.

        Returns:
            Optional[User]: The entity object or None if not found.
        """
        pass

    @abstractmethod
    async def list_paginated(self, offset: int, limit: int) -> PaginatedResult[User]:
        """
        Retrieve a paginated list of User objects.

        Args:
            offset (int): The starting index of the pagination.
            limit (int): The maximum number of items to retrieve.

        Returns:
            PaginatedResult[User]: A paginated result containing the objects. 
        """
        pass

    @abstractmethod
    async def delete_by_id(self, id: int) -> User:
        """
        Delete a existent User from the database.

        Args:
            id (int): The id of User to be deleted.
        
        Returns:
            User: The deleted entity.
        
        Raises:
            UserNotFoundInDatabase: Id not found in database.
        """
        pass

    @abstractmethod
    async def exists_by_email(self, email: str) -> bool:
        """
        Check if a User with the given email exists in the database.

        Args:
            email (str): The email to check.

        Returns:
            bool: True if a User with the given email exists, False otherwise.
        """
        pass
