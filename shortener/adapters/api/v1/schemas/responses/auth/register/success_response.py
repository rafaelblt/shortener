from pydantic import BaseModel

from shortener.domain.user import User

from shortener.adapters.api.v1.schemas.entities import PublicUserSchema


class SuccessRegisterResponse(BaseModel):
    message: str
    user: PublicUserSchema

    @staticmethod
    def with_domain_user(user: User):
        message = "User registered successfully. Please check your email to verify your account."
        schema = PublicUserSchema.from_domain(user)
        return SuccessRegisterResponse(message=message, user=schema)
