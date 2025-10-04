from fastapi import Depends

from shortener.infra.services.jwt_token import JwtAuthTokenService
from shortener.infra.dependencies.fastapi.repositories import get_user_repository

from shortener.infra.settings import get_settings


TOKEN_PURPOSE = "access"


def make_jwt_access_auth_token_service(
    user_repository = get_user_repository()
):
    return JwtAuthTokenService(
        user_repository=user_repository,
        purpose=TOKEN_PURPOSE,
        expires_in=get_settings().access_token_expiration
    )


def get_access_auth_token_service():
    match get_settings().access_token_service_impl:
        case "jwt": dep_func = make_jwt_access_auth_token_service
        case _: dep_func = make_jwt_access_auth_token_service
    return Depends(dep_func)
