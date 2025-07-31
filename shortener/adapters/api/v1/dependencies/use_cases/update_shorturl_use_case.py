from fastapi import Depends

from shortener.infra.validators.shorturl_validators import ShortURLUpdateValidator
from shortener.use_cases import UpdateShortURLUseCase

from . import make_sqlalchemy_shorturl_repository


def make_update_shorturl_use_case(
    repository = Depends(make_sqlalchemy_shorturl_repository)
):
    return UpdateShortURLUseCase(
        repository=repository,
        validator=ShortURLUpdateValidator(repository=repository)
    )
