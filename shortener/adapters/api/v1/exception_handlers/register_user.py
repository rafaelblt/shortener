from typing import NoReturn

from http import HTTPStatus

from fastapi.exceptions import HTTPException

from shortener.domain.plan.exceptions import PlanNotFoundInDatabaseError
from shortener.domain.user.exceptions import EmailAlreadyExistsError
from shortener.domain.services.exceptions import (
    PasswordMissingDigitError,
    PasswordMissingLowercaseError,
    PasswordMissingSpecialCharError,
    PasswordMissingUppercaseError,
    PasswordTooLongError,
    PasswordTooShortError
)


class RegisterUserExceptionHandler:

    @staticmethod
    def handle(error: Exception) -> NoReturn:
        if isinstance(error, PlanNotFoundInDatabaseError):
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail=f"There is no plan with the given id: {error.plan_id}."
            )
        elif isinstance(error, EmailAlreadyExistsError):
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail=f"The provided email '{error.email}' already exists."
            )
        elif isinstance(error, PasswordMissingDigitError):
            raise HTTPException(
                status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
                detail="The password must contain at least one digit (0-9)."
            )
        elif isinstance(error, PasswordMissingLowercaseError):
            raise HTTPException(
                status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
                detail="The password must contain at least one lowercase letter (a-z)."
            )
        elif isinstance(error, PasswordMissingUppercaseError):
            raise HTTPException(
                status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
                detail="The password must contain at least one uppercase letter (A-Z)."
            )
        elif isinstance(error, PasswordMissingSpecialCharError):
            raise HTTPException(
                status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
                detail="The password must contain at least one special character (!@#$%^&*)."
            )
        elif isinstance(error, PasswordTooShortError):
            raise HTTPException(
                status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
                detail=("The password is too short. It must be at least "
                       f"{error.min_length} characters long.")
            )
        elif isinstance(error, PasswordTooLongError):
            raise HTTPException(
                status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
                detail=("The password is too long. It must be at most "
                       f"{error.max_length} characters long.")
            )
        else:
            raise error
