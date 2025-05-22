from typing import NoReturn

from http import HTTPStatus

from fastapi.exceptions import HTTPException

from shortener.domain.user.exceptions import (
    UserNotFoundInDatabaseError, UserPasswordIncorrectError
)


class LoginUserExceptionHandler:

    @staticmethod
    def handle(error: Exception) -> NoReturn:
        if isinstance(error, (UserNotFoundInDatabaseError, UserPasswordIncorrectError)):
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED,
                detail="Invalid email or password."
            )
        else:
            raise error
