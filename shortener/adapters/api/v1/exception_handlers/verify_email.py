from typing import NoReturn
from http import HTTPStatus
from fastapi import HTTPException

from shortener.domain.services.exceptions import (
    AuthTokenExpiredError,
    AuthTokenInvalidError
)
from shortener.domain.user.exceptions import (
    UserNotFoundInDatabaseError,
    UserStatusInvalidToVerifyEmailError
)

from . import ExceptionHandler


class VerifyEmailExceptionHandler(ExceptionHandler):

    @staticmethod
    def handle(error: Exception) -> NoReturn:
        if isinstance(error, (AuthTokenInvalidError, UserNotFoundInDatabaseError)):
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail="Invalid email verification token."
            )
        elif isinstance(error, AuthTokenExpiredError):
            raise HTTPException(
                status_code=HTTPStatus.GONE,
                detail="Email verification token has expired."
            )
        elif isinstance(error, UserStatusInvalidToVerifyEmailError):
            status = error.status.value
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail=f"Cannot verify email in current user state ({status})."
            )
        else:
            raise error
