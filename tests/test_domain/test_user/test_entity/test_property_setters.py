import pytest

from shortener.domain.user import User
from shortener.domain.user.fields import Name, HashedPassword


def test_set_name(normal_user: User):
    normal_user.name = Name("New Example Name")
    assert normal_user.name == "New Example Name"


def test_set_name_raises_type_error(normal_user: User):
    name = normal_user.name
    with pytest.raises(TypeError):
        normal_user.name = 1
    assert normal_user.name == name


def test_set_hashed_password(normal_user: User):
    normal_user.hashed_password = HashedPassword("newhash")
    assert normal_user.hashed_password == "newhash"


def test_set_hashed_password_raises_type_error(normal_user: User):
    hashed_password = normal_user.hashed_password
    with pytest.raises(TypeError):
        normal_user.hashed_password = 1
    assert normal_user.hashed_password == hashed_password
