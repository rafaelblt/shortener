from abc import ABC, abstractmethod

from shortener.domain.plan import Plan


class PlanRepository(ABC):

    @abstractmethod
    async def add(self, plan: Plan) -> Plan:
        """
        Add a Plan object to the database and return the updated object.

        Args:
            plan (Plan): The object to add.
        
        Returns:
            User: Return the updated object.
        """
        pass

    @abstractmethod
    async def update(self, plan: Plan) -> Plan:
        """
        Update a existent Plan in database.

        Args:
            plan (Plan): The object to update.
        
        Returns:
            Plan: The updated entity.
        
        Raises:
            PlanNotFoundInDatabaseError: Plan not found in database.
        """
        pass

    @abstractmethod
    async def get_all(self) -> list[Plan]:
        """
        Retrieve all Plan objects from the database.

        Returns:
            list[Plan]: A list of all Plan objects.
        """
        pass

    @abstractmethod
    async def get_by_id(self, id: int) -> Plan | None:
        """
        Retrieves a Plan by its id.

        Args:
            id (int): The Plan id.

        Returns:
            Optional[Plan]: The entity object or None if not found.
        """
        pass

    @abstractmethod
    async def delete_by_id(self, id: int) -> Plan:
        """
        Delete a existent Plan from the database.

        Args:
            id (int): The id of Plan to be deleted.
        
        Returns:
            Plan: The deleted entity.
        
        Raises:
            PlanNotFoundInDatabase: Id not found in database.
        """
        pass
