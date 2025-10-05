from shortener.infra.dependencies.fastapi.db.repositories import get_shorturl_repository, get_user_repository
from shortener.use_cases import CreateShortURLForUserUseCase


def make_create_shorturl_for_user_use_case(
    shorturl_repository = get_shorturl_repository(),
    user_repository = get_user_repository()
):
    return CreateShortURLForUserUseCase(
        shorturl_repository=shorturl_repository,
        user_repository=user_repository
    )
