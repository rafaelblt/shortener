from fastapi import Depends

from shortener.infra.services.jwt_token import JwtAuthTokenService
from shortener.infra.settings import get_settings

from shortener.infra.dependencies.fastapi.repositories import get_user_repository


def make_jwt_verify_email_auth_token_service(
    user_repository = get_user_repository()
):
    return JwtAuthTokenService(
        user_repository=user_repository,
        purpose="verify_email",
        expires_in=get_settings().email_verification_expiration
    )


def get_verify_email_auth_token_service():
    match get_settings().verify_email_token_service_impl:
        case "jwt":
            dep_func = make_jwt_verify_email_auth_token_service
        case _:
            dep_func = make_jwt_verify_email_auth_token_service
    return Depends(dep_func)
