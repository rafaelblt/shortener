from abc import ABC, abstractmethod

from shortener.domain.user.fields import HashedPassword


class PasswordHasherService(ABC):

    @abstractmethod
    def hash(self, plain_password: str) -> HashedPassword:
        """Returns the hash of the password."""
        pass

    @abstractmethod
    def verify(self, plain_password: str, hashed_password: str) -> bool:
        """
        Returns True if the plain password matches the hashed password, and 
        False otherwise.
        """
        pass
