import pytest

from fastapi.params import Depends

from shortener.use_cases import GetShortURLUseCase

from shortener.adapters.api.dependencies import (
    make_get_shorturl_use_case, make_sqlalchemy_shorturl_repository
)


@pytest.fixture
def use_case():
    return make_get_shorturl_use_case()


def test_instance(use_case: GetShortURLUseCase):
    assert isinstance(use_case, GetShortURLUseCase)


def test_attr_repository(use_case: GetShortURLUseCase):
    assert isinstance(use_case.repository, Depends)
    assert use_case.repository.dependency == make_sqlalchemy_shorturl_repository
