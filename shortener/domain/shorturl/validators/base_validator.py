from abc import ABC, abstractmethod
from shortener.domain.shorturl import ShortURL


class ShortURLValidator(ABC):
    
    @abstractmethod
    def validate(self, shorturl: ShortURL) -> None:
        pass
