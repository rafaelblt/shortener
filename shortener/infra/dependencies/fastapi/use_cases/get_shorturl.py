from shortener.infra.dependencies.fastapi.db.repositories import get_shorturl_repository
from shortener.use_cases import GetShortURLUseCase


def make_get_shorturl_use_case(
    repository = get_shorturl_repository()
):
    return GetShortURLUseCase(repository=repository)
