from typing import NoReturn
from http import HTTPStatus

from fastapi.exceptions import HTTPException

from shortener.domain.user.exceptions import (
    UserNotFoundError, UserPasswordIncorrectError
)

from . import ExceptionHandler


class LoginUserExceptionHandler(ExceptionHandler):

    @staticmethod
    def handle(error: Exception) -> NoReturn:
        if isinstance(error, (UserNotFoundError, UserPasswordIncorrectError)):
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED,
                detail="Invalid email or password."
            )
        else:
            raise error
