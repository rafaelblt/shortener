from pydantic_core import PydanticCustomError


def get_pydantic_email_invalid_error(input: str):
    return PydanticCustomError(
        "invalid_email", "The User email is invalid.", {"input": input}
    )
