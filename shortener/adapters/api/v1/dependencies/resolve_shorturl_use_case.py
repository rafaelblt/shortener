from fastapi import Depends

from shortener.use_cases import ResolveShortURLUseCase

from .sqlalchemy_shorturl_repository import make_sqlalchemy_shorturl_repository


def make_resolve_shorturl_use_case(
    repository = Depends(make_sqlalchemy_shorturl_repository)
):
    return ResolveShortURLUseCase(repository=repository)
