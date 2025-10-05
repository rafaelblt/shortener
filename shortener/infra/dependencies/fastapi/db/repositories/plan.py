from fastapi import Depends

from shortener.infra.db import get_session
from shortener.infra.db.repositories import SQLAlchemyPlanRepository
from shortener.infra.settings import get_settings


def make_sqlalchemy_plan_repository(session = Depends(get_session)):
    return SQLAlchemyPlanRepository(session=session)


def get_plan_repository():
    match get_settings().plan_repository_impl:
        case "sqlalchemy": f = make_sqlalchemy_plan_repository
        case "test": f = None
        case _: f = make_sqlalchemy_plan_repository
    return Depends(f)
