import pytest

from shortener.domain.user import User
from shortener.domain.user.fields.name import (
    Name, NAME_MAX_LENGTH, NAME_MIN_LENGTH
)

from shortener.adapters.api.v1.validators import validate_name


@pytest.fixture
def str_name(normal_user: User):
    return str(normal_user.name)


def test_instance_retrieved(str_name):
    retrieved = validate_name(str_name)
    assert isinstance(retrieved, Name)


def test_raises_value_error_with_name_longer_than_max_length():
    with pytest.raises(
        ValueError,
        match=f"The User name must be at most {NAME_MAX_LENGTH} characters long."
    ):
        validate_name("a" * (NAME_MAX_LENGTH + 1))


def test_raises_value_error_with_name_shorter_than_min_length():
    with pytest.raises(
        ValueError,
        match=f"The User name must be at least {NAME_MIN_LENGTH} characters long."
    ):
        validate_name("a" * (NAME_MIN_LENGTH - 1))


def test_raises_value_error_with_name_with_invalid_pattern():
    with pytest.raises(
        ValueError, match="The User name does not match the required pattern."
    ):
        validate_name("ml,:æ”→ßŋøøþæßþøæþøŋ→øþ→øþþ→æ”")
