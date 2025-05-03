import pytest

from fastapi.params import Depends

from shortener.adapters.api.v1.dependencies import (
    make_sqlalchemy_plan_repository
)

from shortener.infra.db import get_session
from shortener.infra.db.repositories import SQLAlchemyPlanRepository


@pytest.fixture
def repository():
    return make_sqlalchemy_plan_repository()


def test_instance(repository: SQLAlchemyPlanRepository):
    assert isinstance(repository, SQLAlchemyPlanRepository)


def test_attr_session(repository: SQLAlchemyPlanRepository):
    assert isinstance(repository.session, Depends)
    assert repository.session.dependency == get_session
