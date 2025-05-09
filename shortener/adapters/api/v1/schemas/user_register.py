from typing import Annotated

from shortener.adapters.api.v1.validators import validate_email, validate_name

from pydantic import BaseModel, AfterValidator, ConfigDict


class UserRegisterSchema(BaseModel):
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
