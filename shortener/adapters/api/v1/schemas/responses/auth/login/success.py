from pydantic import BaseModel, Field
from datetime import datetime

from shortener.adapters.api.v1.schemas.entities.user import PublicUserSchema

from shortener.domain.shared.token import Token
from shortener.domain.user import User


class AccessTokenField(BaseModel):
    token: str = Field(..., description="JWT access token")
    token_type: str = Field(..., description="Token type (usually 'bearer')")
    expires_at: datetime = Field(..., description="Token expiration timestamp")
    expires_seconds: int = Field(..., description="Token expiration time in seconds")


class RefreshTokenField(BaseModel):
    token: str = Field(..., description="Refresh token")
    expires_at: datetime = Field(..., description="Token expiration timestamp")
    expires_seconds: int = Field(..., description="Token expiration time in seconds")


class LoginSuccessResponse(BaseModel):
    access_token: AccessTokenField = Field(..., description="Access token data")
    refresh_token: RefreshTokenField = Field(..., description="Refresh token data")
    user: PublicUserSchema = Field(..., description="Authenticated user")

    @classmethod
    def make_response(
        cls,
        access_token: Token,
        refresh_token: Token,
        user: User
    ):
        access_token_field = AccessTokenField(
            token=access_token.value,
            token_type="bearer",
            expires_at=access_token.expires_at,
            expires_seconds=access_token.time_remaining.seconds
        )

        refresh_token_field = RefreshTokenField(
            token=refresh_token.value,
            expires_at=refresh_token.expires_at,
            expires_seconds=refresh_token.time_remaining.seconds
        )

        return cls(
            access_token=access_token_field,
            refresh_token=refresh_token_field,
            user=PublicUserSchema.from_domain(user)
        )
