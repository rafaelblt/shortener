from abc import ABC, abstractmethod
from shortener.domain.shorturl.shorturl import ShortURL


class ShortURLValidator(ABC):
    
    @abstractmethod
    def validate(self, shorturl: ShortURL) -> None:
        """
        Abstract method to validate ShortURL.

        Args:
            shorturl (ShortURL): The ShortURL object to be validated.
        
        Returns:
            None: The ShortURL is valid.
        
        Raises:
            ShortURLValidationError: If any part of ShortURL is invalid.
        """
        pass
