import pytest

from shortener.domain.user import User
from shortener.domain.user.fields import UserStatus

from shortener.domain.user.exceptions import UserStatusInvalidToVerifyEmailError


def test_with_active_user(normal_user: User):
    with pytest.raises(UserStatusInvalidToVerifyEmailError) as error:
        normal_user.verify_email()
    assert error.value.status == normal_user.status
    assert error.value.required_status == UserStatus.UNVERIFIED_EMAIL


def test_with_suspended_user(suspended_user: User):
    with pytest.raises(UserStatusInvalidToVerifyEmailError) as error:
        suspended_user.verify_email()
    assert error.value.status == suspended_user.status
    assert error.value.required_status == UserStatus.UNVERIFIED_EMAIL


def test_with_banned_user(banned_user: User):
    with pytest.raises(UserStatusInvalidToVerifyEmailError) as error:
        banned_user.verify_email()
    assert error.value.status == banned_user.status
    assert error.value.required_status == UserStatus.UNVERIFIED_EMAIL


def test_with_locked_user(locked_user: User):
    with pytest.raises(UserStatusInvalidToVerifyEmailError) as error:
        locked_user.verify_email()
    assert error.value.status == locked_user.status
    assert error.value.required_status == UserStatus.UNVERIFIED_EMAIL


def test_with_valid_status(unverified_email_user: User):
    user = unverified_email_user
    assert user.verify_email() is None
    assert user.status == UserStatus.ACTIVE
