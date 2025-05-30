import pytest
from shortener.domain.user import User
from shortener.domain.user.exceptions import (
    UserEmailNotVerifiedError,
    UserSuspendedError,
    UserBannedError,
    UserLockedError
)


def test_ensure_can_login(normal_user: User):
    assert normal_user.ensure_can_login() is None


def test_ensure_can_login_with_unverified_email_user(
    unverified_email_user: User
):
    with pytest.raises(UserEmailNotVerifiedError):
        unverified_email_user.ensure_can_login()


def test_ensure_can_login_with_suspended_user(suspended_user: User):
    with pytest.raises(UserSuspendedError):
        suspended_user.ensure_can_login()


def test_ensure_can_login_with_banned_user(banned_user: User):
    with pytest.raises(UserBannedError):
        banned_user.ensure_can_login()


def test_ensure_can_login_with_locked_user(locked_user: User):
    with pytest.raises(UserLockedError):
        locked_user.ensure_can_login()
