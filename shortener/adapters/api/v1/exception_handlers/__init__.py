from abc import ABC, abstractmethod
from typing import NoReturn


class ExceptionHandler(ABC):

    @staticmethod
    @abstractmethod
    def handle(error: Exception) -> NoReturn:
        raise error


from .register_user import RegisterUserExceptionHandler
from .login_user import LoginUserExceptionHandler
from .verify_email import VerifyEmailExceptionHandler
