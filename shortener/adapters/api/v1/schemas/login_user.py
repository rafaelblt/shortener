from typing import Annotated

from shortener.domain.user.fields import Email
from shortener.domain.user.exceptions import UserValidationError

from pydantic import BaseModel, AfterValidator, ConfigDict


def validate_email(value: str) -> Email:
    try:
        return Email(value)
    except UserValidationError as e:
        raise ValueError(str(e))


class LoginUserSchema(BaseModel):
    email: Annotated[str, AfterValidator(validate_email)]
    password: str
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "user@example.com",
                "password": "pass123"
            }
        }
    )