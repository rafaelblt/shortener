from pydantic import BaseModel, Field
from typing import Literal


class SuccessLoginResponse(BaseModel):
    access_token: str = Field(..., description="JWT access token")
    token_type: Literal["bearer"] = Field(
        ..., description="Token type (usually 'bearer')"
    )
    expires_minutes: int = Field(
        ..., description="Token expiration time in minutes"
    )
    email: str = Field(..., description="Authenticated user email")
