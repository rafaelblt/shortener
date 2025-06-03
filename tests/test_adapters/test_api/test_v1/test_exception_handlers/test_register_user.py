import pytest
import re

from http import HTTPStatus
from fastapi import HTTPException

from shortener.domain.plan.exceptions import PlanNotFoundError
from shortener.domain.user.exceptions import EmailAlreadyExistsError
from shortener.domain.services.exceptions import (
    PasswordMissingDigitError,
    PasswordMissingLowercaseError,
    PasswordMissingSpecialCharError,
    PasswordMissingUppercaseError,
    PasswordTooLongError,
    PasswordTooShortError
)

from .utils import test_raise_unhandled_exception

from shortener.adapters.api.v1.exception_handlers import RegisterUserExceptionHandler


@pytest.fixture
def exception_handler():
    return RegisterUserExceptionHandler


def test_plan_not_found_in_database(exception_handler: RegisterUserExceptionHandler):
    with pytest.raises(
        HTTPException, match="There is no plan with the given id: 1."
    ) as http_error:
        exception_handler.handle(PlanNotFoundError(plan_id=1))
    assert http_error.value.status_code == HTTPStatus.BAD_REQUEST


def test_email_already_exists(exception_handler: RegisterUserExceptionHandler):
    with pytest.raises(
        HTTPException, match="The provided email 'test' already exists."
    ) as http_error:
        exception_handler.handle(EmailAlreadyExistsError(email="test"))
    assert http_error.value.status_code == HTTPStatus.CONFLICT


def test_password_missing_digit(exception_handler: RegisterUserExceptionHandler):   
    with pytest.raises(
        HTTPException,
        match=re.escape("422: The password must contain at least one digit (0-9).")
    ) as http_error:
        exception_handler.handle(PasswordMissingDigitError(value="pass"))
    assert http_error.value.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_password_missing_lowercase(exception_handler: RegisterUserExceptionHandler):
    with pytest.raises(
        HTTPException,
        match=re.escape("422: The password must contain at least one lowercase "
                        "letter (a-z).")
    ) as http_error:
        exception_handler.handle(PasswordMissingLowercaseError(value="pass"))
    assert http_error.value.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_password_missing_uppercase(exception_handler: RegisterUserExceptionHandler):
    with pytest.raises(
        HTTPException,
        match=re.escape("422: The password must contain at least one uppercase "
                        "letter (A-Z).")
    ) as http_error:
        exception_handler.handle(PasswordMissingUppercaseError(value="pass"))
    assert http_error.value.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_password_missing_special_char(exception_handler: RegisterUserExceptionHandler):
    with pytest.raises(
        HTTPException,
        match=re.escape("422: The password must contain at least one special "
                        "character (!@#$%^&*).")
    ) as http_error:
        exception_handler.handle(PasswordMissingSpecialCharError(value="pass"))
    assert http_error.value.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_password_too_short(exception_handler: RegisterUserExceptionHandler):
    with pytest.raises(
        HTTPException,
        match="422: The password is too short. It must be at least 1 characters long."
    ) as http_error:
        exception_handler.handle(PasswordTooShortError(value="pass", min_length=1))
    assert http_error.value.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_password_too_long(exception_handler: RegisterUserExceptionHandler):
    with pytest.raises(
        HTTPException,
        match="422: The password is too long. It must be at most 1 characters long."
    ) as http_error:
        exception_handler.handle(PasswordTooLongError(value="pass", max_length=1))
    assert http_error.value.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_unhandled_exception(exception_handler: RegisterUserExceptionHandler):
    test_raise_unhandled_exception(exception_handler)
