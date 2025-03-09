import pytest

from fastapi.params import Depends

from shortener.use_cases import DeleteShortURLUseCase

from shortener.adapters.api.v1.dependencies import (
    make_delete_shorturl_use_case, make_sqlalchemy_shorturl_repository
)


@pytest.fixture
def use_case():
    return make_delete_shorturl_use_case()


def test_instance(use_case: DeleteShortURLUseCase):
    assert isinstance(use_case, DeleteShortURLUseCase)


def test_attr_repository(use_case: DeleteShortURLUseCase):
    assert isinstance(use_case.repository, Depends)
    assert use_case.repository.dependency == make_sqlalchemy_shorturl_repository
