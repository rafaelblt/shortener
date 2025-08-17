import pytest

from fastapi.params import Depends

from shortener.use_cases import UpdateShortURLUseCase

from shortener.infra.validators.shorturl_validators import ShortURLUpdateValidator

from shortener.adapters.api.v1.dependencies import (
    make_update_shorturl_use_case,
    make_sqlalchemy_shorturl_repository
)


@pytest.fixture
def use_case():
    return make_update_shorturl_use_case()


def test_instance(use_case: UpdateShortURLUseCase):
    assert isinstance(use_case, UpdateShortURLUseCase)


def test_attr_shorturl_repository(use_case: UpdateShortURLUseCase):
    assert isinstance(use_case.shorturl_repository, Depends)
    assert (
        use_case.shorturl_repository.dependency == 
        make_sqlalchemy_shorturl_repository
    )


def test_attr_validators_map(use_case: UpdateShortURLUseCase):
    assert use_case.validators_map == {}
