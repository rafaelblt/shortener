import pytest

from fastapi.params import Depends

from shortener.adapters.api.v1.dependencies import (
    make_sqlalchemy_user_repository
)

from shortener.infra.db import get_session
from shortener.infra.db.repositories import SQLAlchemyUserRepository


@pytest.fixture
def repository():
    return make_sqlalchemy_user_repository()


def test_instance(repository: SQLAlchemyUserRepository):
    assert isinstance(repository, SQLAlchemyUserRepository)


def test_attr_session(repository: SQLAlchemyUserRepository):
    assert isinstance(repository.session, Depends)
    assert repository.session.dependency == get_session
