from fastapi import Depends

from shortener.use_cases import UpdateShortURLUseCase

from . import make_sqlalchemy_shorturl_repository


def make_update_shorturl_use_case(
    shorturl_repository = Depends(make_sqlalchemy_shorturl_repository)
):
    return UpdateShortURLUseCase(
        shorturl_repository=shorturl_repository,
        validators_map={}
    )
