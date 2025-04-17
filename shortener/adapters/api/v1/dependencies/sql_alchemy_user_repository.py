from fastapi import Depends

from shortener.infra.db import get_session
from shortener.infra.db.repositories import SQLAlchemyUserRepository


def make_sqlalchemy_user_repository(session = Depends(get_session)):
    return SQLAlchemyUserRepository(session=session)
