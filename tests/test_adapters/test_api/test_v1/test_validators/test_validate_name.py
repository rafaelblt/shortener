import pytest

from pydantic_core import PydanticCustomError

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


def test_raises_error_with_name_longer_than_max_length():
    with pytest.raises(PydanticCustomError) as error:
        validate_name("a" * (NAME_MAX_LENGTH + 1))
    assert isinstance(error.value.context, dict)
    assert error.value.context["max_length"] == NAME_MAX_LENGTH


def test_raises_error_with_name_shorter_than_min_length():
    with pytest.raises(PydanticCustomError) as error:
        validate_name("a" * (NAME_MIN_LENGTH - 1))
    assert isinstance(error.value.context, dict)
    assert error.value.context["min_length"] == NAME_MIN_LENGTH


def test_raises_error_with_name_with_invalid_pattern():
    with pytest.raises(PydanticCustomError) as error:
        validate_name("ml,:æ”→ßŋøøþæßþøæþøŋ→øþ→øþþ→æ”")
    assert isinstance(error.value.context, dict)
    assert error.value.message() == "The User name does not match the required pattern."
