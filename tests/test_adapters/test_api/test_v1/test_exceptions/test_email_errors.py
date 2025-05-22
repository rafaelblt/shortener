from pydantic_core import PydanticCustomError

from shortener.adapters.api.v1.exceptions import get_pydantic_email_invalid_error


def test_pydantic_email_invalid_error():
    retrieved = get_pydantic_email_invalid_error("test")
    assert isinstance(retrieved, PydanticCustomError)
    assert retrieved.message() == "The User email is invalid."
    assert retrieved.type == "invalid_email"
    assert isinstance(retrieved.context, dict)
    assert retrieved.context["input"] == "test"
