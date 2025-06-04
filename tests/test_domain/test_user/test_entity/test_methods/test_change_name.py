import pytest

from shortener.domain.user import User
from shortener.domain.user.fields import Name
from shortener.domain.user.exceptions import UserAttributeTypeError


def test_change_name(normal_user: User):
    normal_user.change_name(Name("New Example Name"))
    assert normal_user.name == "New Example Name"


def test_change_name_raises_validation_error(normal_user: User):
    with pytest.raises(UserAttributeTypeError):
        normal_user.change_name("new name")
