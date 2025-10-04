from shortener.infra.dependencies.fastapi.repositories import get_shorturl_repository
from shortener.use_cases import CreateShortURLForUserUseCase


def make_create_shorturl_for_user_use_case(
    shorturl_repository = get_shorturl_repository()
):
    return CreateShortURLForUserUseCase(shorturl_repository=shorturl_repository)
