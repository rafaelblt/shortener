import pytest

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
from shortener.domain.user.fields import UserStatus

from .utils import test_raise_unhandled_exception

from shortener.adapters.api.v1.exception_handlers import VerifyEmailExceptionHandler


@pytest.fixture
def exception_handler():
    return VerifyEmailExceptionHandler


def test_auth_token_invalid(exception_handler: VerifyEmailExceptionHandler):
    with pytest.raises(
        HTTPException, match="Invalid email verification token."
    ) as http_error:
        exception_handler.handle(AuthTokenInvalidError())
    assert http_error.value.status_code == HTTPStatus.BAD_REQUEST


def test_user_not_found(exception_handler: VerifyEmailExceptionHandler):
    with pytest.raises(
        HTTPException, match="Invalid email verification token."
    ) as http_error:
        exception_handler.handle(UserNotFoundInDatabaseError(field="e", value="t"))
    assert http_error.value.status_code == HTTPStatus.BAD_REQUEST


def test_auth_token_expired(exception_handler: VerifyEmailExceptionHandler):
    with pytest.raises(
        HTTPException, match="Email verification token has expired."
    ) as http_error:
        exception_handler.handle(AuthTokenExpiredError())
    assert http_error.value.status_code == HTTPStatus.GONE


def test_user_status_invalid(exception_handler: VerifyEmailExceptionHandler):
    status = UserStatus.ACTIVE
    required_status = UserStatus.UNVERIFIED_EMAIL
    with pytest.raises(HTTPException) as http_error:
        exception_handler.handle(UserStatusInvalidToVerifyEmailError(
            status=status, required_status=required_status
        ))
    assert http_error.value.status_code == HTTPStatus.CONFLICT
    assert (
        http_error.value.detail == 
        f"Cannot verify email in current user state ({status.value})."
    )


def test_unhandled_exception(exception_handler: VerifyEmailExceptionHandler):
    test_raise_unhandled_exception(exception_handler)
