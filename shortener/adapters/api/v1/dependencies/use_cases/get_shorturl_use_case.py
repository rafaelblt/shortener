from fastapi import Depends

from . import make_sqlalchemy_shorturl_repository

from shortener.use_cases import GetShortURLUseCase


def make_get_shorturl_use_case(
    repository = Depends(make_sqlalchemy_shorturl_repository)    
):
    return GetShortURLUseCase(repository=repository)
