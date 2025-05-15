import pytest

from shortener.domain.shared.datetime_utils import utc_now

from shortener.domain.user import User
from shortener.domain.user.fields import HashedPassword
from shortener.domain.user.exceptions import UserAttributeTypeError


def test_update_last_login(normal_user: User):
    old_last_login = normal_user.last_login
    expected = utc_now()
    timef = "%d/%m/%Y, %H:%M:%S"

    normal_user.update_last_login()

    assert old_last_login != normal_user.last_login
    assert normal_user.last_login.strftime(timef) == expected.strftime(timef)


def test_change_hashed_password(normal_user: User):
    normal_user.change_hashed_password(HashedPassword("new-hashed-password"))
    assert normal_user.hashed_password == "new-hashed-password"


def test_change_hashed_password_raises_validation_error(normal_user: User):
    with pytest.raises(UserAttributeTypeError):
        normal_user.change_hashed_password("new-hashed-password")
