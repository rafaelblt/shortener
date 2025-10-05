from shortener.infra.dependencies.fastapi.db.repositories import get_shorturl_repository
from shortener.use_cases import CreateShortURLUseCase


def make_create_shorturl_use_case(
    shorturl_repository = get_shorturl_repository()
):
    return CreateShortURLUseCase(shorturl_repository=shorturl_repository)

