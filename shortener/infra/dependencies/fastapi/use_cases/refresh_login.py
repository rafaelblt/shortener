from shortener.use_cases import RefreshLoginUseCase
from shortener.infra.dependencies.fastapi.services import (
    get_access_auth_token_service,
    get_refresh_auth_token_service,
)


def make_refresh_login_use_case(
    access_token_service = get_access_auth_token_service(),
    refresh_token_service = get_refresh_auth_token_service(),
):
    return RefreshLoginUseCase(
        access_token_service=access_token_service,
        refresh_token_service=refresh_token_service
    )
