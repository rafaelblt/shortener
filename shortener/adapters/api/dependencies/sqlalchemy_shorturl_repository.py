from fastapi import Depends

from shortener.infra.db import get_session
from shortener.infra.db.repositories import SQLAlchemyShortURLRepository


def make_sqlalchemy_shorturl_repository(session = Depends(get_session)):
    return SQLAlchemyShortURLRepository(session=session)
