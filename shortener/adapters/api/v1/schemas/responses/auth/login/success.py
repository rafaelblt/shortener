from typing import Literal
from pydantic import BaseModel, Field
from datetime import datetime, timedelta

from shortener.adapters.api.v1.schemas.entities.user import PublicUserSchema
from shortener.domain.shared.datetime_utils import utc_now
from shortener.domain.user.user import User


class AccessTokenField(BaseModel):
    token: str = Field(..., description="JWT access token")
    token_type: Literal["bearer"] = Field(..., description="Token type (usually 'bearer')")
    expires_at: datetime = Field(..., description="Token expiration timestamp")
    expires_seconds: int = Field(..., description="Token expiration time in seconds")


class RefreshTokenField(BaseModel):
    token: str = Field(..., description="Refresh token")
    expires_at: datetime = Field(..., description="Token expiration timestamp")
    expires_seconds: int = Field(..., description="Token expiration time in seconds")


class SuccessLoginResponse(BaseModel):
    access_token: AccessTokenField = Field(..., description="Access token data")
    refresh_token: RefreshTokenField = Field(..., description="Refresh token data")
    user: PublicUserSchema = Field(..., description="Authenticated user")

    @classmethod
    def make_response(
        cls,
        access_token: str,
        access_token_type: str,
        access_token_expires_in: timedelta,
        refresh_token: str,
        refresh_token_expires_in: timedelta,
        user: User
    ):
        access_token_field = AccessTokenField(
            token=access_token,
            token_type="bearer",
            expires_at=utc_now() + access_token_expires_in,
            expires_seconds=access_token_expires_in.seconds
        )

        refresh_token_field = RefreshTokenField(
            token=refresh_token,
            expires_at=utc_now() + refresh_token_expires_in,
            expires_seconds=refresh_token_expires_in.seconds
        )

        return cls(
            access_token=access_token_field,
            refresh_token=refresh_token_field,
            user=PublicUserSchema.from_domain(user)
        )
