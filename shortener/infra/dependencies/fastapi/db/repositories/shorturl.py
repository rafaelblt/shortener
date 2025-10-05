from fastapi import Depends

from shortener.infra.db import get_session
from shortener.infra.db.repositories import SQLAlchemyShortURLRepository
from shortener.infra.settings import get_settings


def make_sqlalchemy_shorturl_repository(session = Depends(get_session)):
    return SQLAlchemyShortURLRepository(session=session)


def get_shorturl_repository():
    match get_settings().shorturl_repository_impl:
        case "sqlalchemy": f = make_sqlalchemy_shorturl_repository
        case _: f = make_sqlalchemy_shorturl_repository
    return Depends(f)
