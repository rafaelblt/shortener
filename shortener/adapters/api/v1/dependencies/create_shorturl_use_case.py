from fastapi import Depends

from .sqlalchemy_shorturl_repository import make_sqlalchemy_shorturl_repository
from .sqlalchemy_user_repository import make_sqlalchemy_user_repository

from shortener.infra.validators.shorturl_create_validator import ShortURLCreateValidator

from shortener.use_cases import CreateShortURLUseCase


def make_create_shorturl_use_case(
    shorturl_repository = Depends(make_sqlalchemy_shorturl_repository),
    user_repository = Depends(make_sqlalchemy_user_repository)
):
    return CreateShortURLUseCase(
        shorturl_repository=shorturl_repository,
        user_repository=user_repository,
        validator=ShortURLCreateValidator(repository=shorturl_repository)
    )
