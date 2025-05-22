import pytest

from pydantic_core import PydanticCustomError

from shortener.domain.user import User
from shortener.domain.user.fields import Email

from shortener.adapters.api.v1.validators import validate_email


@pytest.fixture
def str_email(normal_user: User):
    return str(normal_user.email)


def test_instance_retrieved(str_email):
    retrieved = validate_email(str_email)
    assert isinstance(retrieved, Email)


def test_raises_value_error_with_invalid_email():
    with pytest.raises(PydanticCustomError) as error:
        validate_email("invalid@invalid")
    assert error.value.message() == "The User email is invalid."
