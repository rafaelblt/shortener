from typing import Annotated

from shortener.domain.shared.primarykey import PrimaryKey
from shortener.domain.user.fields import Email, Name, PlainPassword
from shortener.adapters.api.v1.validators import CustomAfterValidator

from pydantic import BaseModel, AfterValidator, ConfigDict


EmailValidator = CustomAfterValidator(Email.validate_email)
NameValidator = CustomAfterValidator(Name.validate_name)
PasswordValidator = CustomAfterValidator(PlainPassword.validate_password)


class RegisterPayload(BaseModel):
    email: Annotated[str, AfterValidator(EmailValidator)]
    name: Annotated[str, AfterValidator(NameValidator)]
    password: Annotated[str, AfterValidator(PasswordValidator)]
    plan_id: int
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "user@example.com",
                "name": "User Name Example",
                "password": "Pass123",
                "plan_id": 1
            }
        }
    )

    def get_email(self) -> Email:
        return Email(self.email)
    
    def get_name(self) -> Name:
        return Name(self.name)
    
    def get_password(self) -> PlainPassword:
        return PlainPassword(self.password)
    
    def get_plan_pk(self) -> PrimaryKey:
        return PrimaryKey.create_pk_id(self.plan_id)
