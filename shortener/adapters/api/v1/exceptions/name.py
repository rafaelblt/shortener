from pydantic_core import PydanticCustomError


def get_pydantic_name_too_long_error(input: str, max_length: int):
    return PydanticCustomError(
        "invalid_name",
        "The User name must be at most {max_length} characters long.",
        {"input": input, "max_length": max_length}
    )


def get_pydantic_name_too_short_error(input: str, min_length: int):
    return PydanticCustomError(
        "invalid_name",
        "The User name must be at least {min_length} characters long.",
        {"input": input, "min_length": min_length}
    )


def get_pydantic_name_invalid_pattern_error(input: str):
    return PydanticCustomError(
        "invalid_name",
        "The User name does not match the required pattern.",
        {"input": input}
    )