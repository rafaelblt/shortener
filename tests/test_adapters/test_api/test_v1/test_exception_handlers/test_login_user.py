import pytest

from http import HTTPStatus
from fastapi import HTTPException

from shortener.domain.user.exceptions import (
    UserNotFoundError, UserPasswordIncorrectError
)

from .utils import test_raise_unhandled_exception

from shortener.adapters.api.v1.exception_handlers import LoginUserExceptionHandler


@pytest.fixture
def exception_handler():
    return LoginUserExceptionHandler


def test_user_not_found_in_database(exception_handler: LoginUserExceptionHandler):
    with pytest.raises(
        HTTPException, match="Invalid email or password."
    ) as http_error:
        exception_handler.handle(UserNotFoundError(field="id", value=1))
    assert http_error.value.status_code == HTTPStatus.UNAUTHORIZED


def test_user_password_incorrect(exception_handler: LoginUserExceptionHandler):
    with pytest.raises(
        HTTPException, match="Invalid email or password."
    ) as http_error:
        exception_handler.handle(UserPasswordIncorrectError())
    assert http_error.value.status_code == HTTPStatus.UNAUTHORIZED


def test_unhandled_exception(exception_handler: LoginUserExceptionHandler):
    test_raise_unhandled_exception(exception_handler)
