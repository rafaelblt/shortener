from abc import ABC, abstractmethod
from typing import NoReturn


class ExceptionHandler(ABC):

    @staticmethod
    @abstractmethod
    def handle(error: Exception) -> NoReturn:
        raise error


from .verify_email import VerifyEmailExceptionHandler

from .utils import register_exception_handlers
