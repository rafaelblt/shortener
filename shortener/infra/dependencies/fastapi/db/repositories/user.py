from fastapi import Depends

from shortener.infra.db.session import get_session
from shortener.infra.db.repositories import SQLAlchemyUserRepository

from shortener.infra.settings import get_settings


def make_sqlalchemy_user_repository(
    session = Depends(get_session)
):
    return SQLAlchemyUserRepository(session=session)


def get_user_repository():
    match get_settings().user_repository_impl:
        case "sqlalchemy":
            dep_func = make_sqlalchemy_user_repository
        case _:
            dep_func = make_sqlalchemy_user_repository
    return Depends(dep_func)
