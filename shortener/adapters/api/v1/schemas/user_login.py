from typing import Annotated

from shortener.adapters.api.v1.validators import validate_email

from pydantic import BaseModel, AfterValidator, ConfigDict


class UserLoginSchema(BaseModel):
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