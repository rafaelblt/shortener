from shortener.infra.dependencies.fastapi.services import (
    get_access_auth_token_service,
    get_refresh_auth_token_service,
    get_password_hasher_service
)
from shortener.infra.dependencies.fastapi.repositories import get_user_repository
from shortener.use_cases import LoginUserUseCase



def make_login_user_use_case(
    access_token_service = get_access_auth_token_service(),
    refresh_token_service = get_refresh_auth_token_service(),
    user_repository = get_user_repository(),
    password_hasher_service = get_password_hasher_service()
):
    return LoginUserUseCase(
        user_repository=user_repository,
        password_hasher=password_hasher_service,
        access_token_service=access_token_service,
        refresh_token_service=refresh_token_service
    )
