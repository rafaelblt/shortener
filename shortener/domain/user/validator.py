from abc import ABC, abstractmethod
from shortener.domain.user.user import User


class UserValidator(ABC):
    
    @abstractmethod
    def validate(self, user: User) -> None:
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
