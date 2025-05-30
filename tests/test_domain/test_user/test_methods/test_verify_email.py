import pytest

from shortener.domain.user import User
from shortener.domain.user.fields import UserStatus

from shortener.domain.user.exceptions import UserStatusInvalidToVerifyEmailError


@pytest.mark.parametrize(
    "status",
    [
        UserStatus.ACTIVE,
        UserStatus.BANNED,
        UserStatus.LOCKED,
        UserStatus.SUSPENDED
    ],
)
def test_with_invalid_status(normal_user: User, status: UserStatus):
    normal_user._status = status
    with pytest.raises(UserStatusInvalidToVerifyEmailError) as error:
        normal_user.verify_email()
    assert error.value.status == status
    assert error.value.required_status == UserStatus.EMAIL_UNVERIFIED


def test_with_valid_status(unverified_email_user: User):
    user = unverified_email_user
    assert user.verify_email() is None
    assert user.status == UserStatus.ACTIVE
