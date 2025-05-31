from typing import Annotated

from shortener.domain.user.fields import Email
from shortener.adapters.api.v1.validators import validate_email

from pydantic import BaseModel, AfterValidator, ConfigDict


class LoginRequest(BaseModel):
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

    def get_email(self) -> Email:
        assert isinstance(self.email, Email)
        return self.email
