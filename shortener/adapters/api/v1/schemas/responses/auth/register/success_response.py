from pydantic import BaseModel

from shortener.domain.user import User

from shortener.adapters.api.v1.schemas.entities import PublicUserSchema


class RegisterSuccessResponse(BaseModel):
    message: str
    user: PublicUserSchema

    @classmethod
    def with_domain_user(cls, user: User):
        message = "User registered successfully. Please check your email to verify your account."
        schema = PublicUserSchema.from_domain(user)
        return cls(message=message, user=schema)
