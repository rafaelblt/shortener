from abc import ABC, abstractmethod

from shortener.domain.refresh_token import RefreshToken
from shortener.domain.refresh_token.exceptions import RefreshTokenNotFoundError
from shortener.domain.shared.primarykey import PrimaryKey


class RefreshTokenRepository(ABC):
    EntityType = RefreshToken
    exceptions = {
        "entity_not_found": RefreshTokenNotFoundError
    }

    @abstractmethod
    async def add(self, refresh_token: RefreshToken) -> RefreshToken:
        """
        Add a RefreshToken object to the database and return the updated object.

        Args:
            refresh_token (RefreshToken): The object to add.
        
        Returns:
            RefreshToken: Return the added object.
        """
        pass

    @abstractmethod
    async def update(self, refresh_token: RefreshToken) -> RefreshToken:
        """
        Update a existent RefreshToken in database.

        Args:
            refresh_token (RefreshToken): The object to update.
        
        Returns:
            RefreshToken: The updated entity.
        
        Raises:
            RefreshTokenNotFoundError: Token not found in database.
        """
        pass

    @abstractmethod
    async def get_by_pk(self, pk: PrimaryKey) -> RefreshToken | None:
        """
        Retrieves a RefreshToken by its pk.

        Args:
            pk (PrimaryKey): The RefreshToken pk.

        Returns:
            Optional[RefreshToken]: The entity object or None if not found.
        """
        pass

    @abstractmethod
    async def get_by_token(self, token: str) -> RefreshToken | None:
        """
        Retrieves a RefreshToken by its token.

        Args:
            token (str): The RefreshToken token.

        Returns:
            Optional[RefreshToken]: The entity object or None if not found.
        """
        pass