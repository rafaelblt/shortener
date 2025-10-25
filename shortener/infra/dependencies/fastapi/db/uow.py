from fastapi import Depends

from shortener.infra.db import get_session
from shortener.infra.db.sqlalchemy_uow import SQLAlchemyUnitOfWork


def make_sqlalchemy_unit_of_work(
    session = Depends(get_session)
):
    return SQLAlchemyUnitOfWork(session)


def get_unit_of_work():
    return Depends(make_sqlalchemy_unit_of_work)
