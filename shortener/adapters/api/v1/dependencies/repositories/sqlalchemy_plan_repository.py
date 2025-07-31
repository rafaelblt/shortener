from fastapi import Depends

from shortener.infra.db import get_session
from shortener.infra.db.repositories import SQLAlchemyPlanRepository


def make_sqlalchemy_plan_repository(session = Depends(get_session)):
    return SQLAlchemyPlanRepository(session=session)
