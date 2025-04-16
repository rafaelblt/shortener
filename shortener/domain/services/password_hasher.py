from abc import ABC, abstractmethod


class PasswordHasher(ABC):

    @abstractmethod
    def hash(self, plain_password: str) -> str:
        """Returns the hash of the password."""
        pass

    @abstractmethod
    def verify(self, plain_password: str, hashed_password: str) -> bool:
        """
        Returns True if the plain password matches the hashed password, and 
        False otherwise.
        """
        pass
