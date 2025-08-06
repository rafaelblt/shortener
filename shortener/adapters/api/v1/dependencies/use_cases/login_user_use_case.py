from typing import Annotated
from fastapi import Depends

from shortener.infra.settings import settings
from shortener.infra.services.urlsafe_token import URLSafeTokenGenerator
from shortener.infra.services.jwt_token import JwtTokenService

from shortener.use_cases import LoginUserUseCase

from . import (
    make_sqlalchemy_user_repository,
    make_sqlalchemy_refresh_token_repository,
    make_passlib_password_hasher
)


def make_login_user_use_case(
    user_repository = Depends(make_sqlalchemy_user_repository),
    refresh_token_repository = Depends(make_sqlalchemy_refresh_token_repository),
    password_hasher = Depends(make_passlib_password_hasher)
):
    access_expires_in = settings.ACCESS_TOKEN_EXPIRATION
    refresh_expires_in = settings.REFRESH_TOKEN_EXPIRATION
    return LoginUserUseCase(
        user_repository=user_repository,
        refresh_token_repository=refresh_token_repository,
        password_hasher=password_hasher,
        access_token_service=JwtTokenService(),
        access_token_expires_in=access_expires_in,
        refresh_token_generator=URLSafeTokenGenerator(),
        refresh_token_expires_in=refresh_expires_in
    )


LoginUserUseCaseDependency = Annotated[
    LoginUserUseCase, Depends(make_login_user_use_case)
]
