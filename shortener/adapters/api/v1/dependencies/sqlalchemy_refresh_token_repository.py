from fastapi import Depends

from shortener.infra.db import get_session
from shortener.infra.db.repositories import SQLAlchemyRefreshTokenRepository


def make_sqlalchemy_refresh_token_repository(session = Depends(get_session)):
    return SQLAlchemyRefreshTokenRepository(session=session)
