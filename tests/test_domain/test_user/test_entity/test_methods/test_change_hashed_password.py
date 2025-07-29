import pytest

from shortener.domain.user import User
from shortener.domain.user.fields import HashedPassword
from shortener.domain.user.exceptions import UserAttributeTypeError


def test_change_hashed_password(normal_user: User):
    normal_user.change_hashed_password(HashedPassword("new-hashed-password"))
    assert normal_user.hashed_password == "new-hashed-password"


def test_change_hashed_password_raises_validation_error(normal_user: User):
    with pytest.raises(UserAttributeTypeError):
        normal_user.change_hashed_password("new-hashed-password") # type: ignore
