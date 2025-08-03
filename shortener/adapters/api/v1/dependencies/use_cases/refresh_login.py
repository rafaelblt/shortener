from typing import Annotated
from fastapi import Depends

from shortener.infra.services.urlsafe_token import URLSafeTokenGenerator
from shortener.infra.settings import settings
from shortener.infra.services.jwt_token import JwtTokenService

from shortener.use_cases import RefreshLoginUseCase

from . import make_sqlalchemy_refresh_token_repository


def make_refresh_login_use_case(
    refresh_token_repository = Depends(make_sqlalchemy_refresh_token_repository)
):
    access_expires_in = settings.ACCESS_TOKEN_EXPIRATION
    refresh_expires_in = settings.REFRESH_TOKEN_EXPIRATION
    use_case = RefreshLoginUseCase(
        refresh_token_repository=refresh_token_repository,
        access_token_service=JwtTokenService(),
        access_token_expires_in=access_expires_in,
        refresh_token_generator=URLSafeTokenGenerator(),
        refresh_token_expires_in=refresh_expires_in
    )
    return use_case


RefreshLoginUseCaseDependency = Annotated[
    RefreshLoginUseCase, Depends(make_refresh_login_use_case)
]
