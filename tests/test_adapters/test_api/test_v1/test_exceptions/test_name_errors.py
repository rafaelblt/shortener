from pydantic_core import PydanticCustomError

from shortener.adapters.api.v1.exceptions import (
    get_pydantic_name_too_long_error,
    get_pydantic_name_too_short_error,
    get_pydantic_name_invalid_pattern_error
)


def test_pydantic_name_too_short_error():
    retrieved = get_pydantic_name_too_short_error("test", 10)
    assert isinstance(retrieved, PydanticCustomError)
    assert isinstance(retrieved.context, dict)
    assert retrieved.context["input"] == "test"
    assert retrieved.context["min_length"] == 10
    assert retrieved.type == "invalid_name"
    assert retrieved.message() == "The User name must be at least 10 characters long."


def test_pydantic_name_too_long_error():
    retrieved = get_pydantic_name_too_long_error("test", 10)
    assert isinstance(retrieved, PydanticCustomError)
    assert isinstance(retrieved.context, dict)
    assert retrieved.context["input"] == "test"
    assert retrieved.context["max_length"] == 10
    assert retrieved.type == "invalid_name"
    assert retrieved.message() == "The User name must be at most 10 characters long."


def test_pydantic_name_invalid_pattern_error():
    retrieved = get_pydantic_name_invalid_pattern_error("test")
    assert isinstance(retrieved, PydanticCustomError)
    assert isinstance(retrieved.context, dict)
    assert retrieved.context["input"] == "test"
    assert retrieved.type == "invalid_name"
    assert retrieved.message() == "The User name does not match the required pattern."
