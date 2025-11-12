from typing import Annotated

from shortener.domain.user.fields import Email
from shortener.adapters.api.v1.validators import CustomAfterValidator

from pydantic import BaseModel, AfterValidator, ConfigDict


EmailValidator = CustomAfterValidator(Email.validate_email)


class LoginPayload(BaseModel):
    email: Annotated[str, AfterValidator(EmailValidator)]
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
        return Email(self.email)
