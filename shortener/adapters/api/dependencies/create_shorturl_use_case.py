from fastapi import Depends

from .sqlalchemy_shorturl_repository import make_sqlalchemy_shorturl_repository

from shortener.domain.shorturl.validators import GeneralValidator
from shortener.domain.shorturl import SlugGenerator

from shortener.use_cases import CreateShortURLUseCase


def make_create_shorturl_use_case(
    repository = Depends(make_sqlalchemy_shorturl_repository)
):
    return CreateShortURLUseCase(
        repository=repository,
        validator=GeneralValidator(repository=repository),
        slug_generator=SlugGenerator()
    )
