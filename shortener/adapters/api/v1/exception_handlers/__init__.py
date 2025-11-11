from abc import ABC, abstractmethod
from typing import NoReturn


class ExceptionHandler(ABC):

    @staticmethod
    @abstractmethod
    def handle(error: Exception) -> NoReturn:
        raise error
