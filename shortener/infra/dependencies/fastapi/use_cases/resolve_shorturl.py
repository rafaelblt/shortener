from shortener.infra.dependencies.fastapi.repositories import get_shorturl_repository
from shortener.use_cases import ResolveShortURLUseCase


def make_resolve_shorturl_use_case(
    repository = get_shorturl_repository()
):
    return ResolveShortURLUseCase(repository=repository)
