from abc import ABC, abstractmethod
from shortener.domain.user.user import User


@DeprecationWarning
class UserValidator(ABC):
    
    @abstractmethod
    async def validate(self, user: User) -> None:
        """
        Abstract method to validate User.

        Args:
            user (User): The User object to be validated.
        
        Returns:
            None: The User is valid.
        
        Raises:
            UserValidationError: If any part of User is invalid.
        """
        pass
