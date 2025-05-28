from fastapi import Depends

from shortener.infra.services.jwt_auth_token import JwtAuthTokenService

from shortener.use_cases import VerifyEmailUseCase

from .sqlalchemy_user_repository import make_sqlalchemy_user_repository


def make_verify_email_use_case(
    user_repository = Depends(make_sqlalchemy_user_repository),
):
    return VerifyEmailUseCase(
        user_repository=user_repository,
        auth_token_service=JwtAuthTokenService()
    )
