from typing import Annotated

from shortener.domain.user.fields import Email, Name
from shortener.domain.user.exceptions import UserValidationError

from pydantic import BaseModel, AfterValidator, ConfigDict


def validate_email(value: str) -> Email:
    try:
        return Email(value)
    except UserValidationError as e:
        raise ValueError(str(e))
    

def validate_name(value: str) -> Name:
    try:
        return Name(value)
    except UserValidationError as e:
        raise ValueError(str(e))


class RegisterUserSchema(BaseModel):
    email: Annotated[str, AfterValidator(validate_email)]
    name: Annotated[str, AfterValidator(validate_name)]
    password: str
    plan_id: int
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "user@example.com",
                "name": "User Name Example",
                "password": "pass123",
                "plan_id": 1
            }
        }
    )
