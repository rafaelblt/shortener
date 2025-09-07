import pytest

from fastapi.params import Depends

from shortener.use_cases import CreateShortURLUseCase

from shortener.adapters.api.v1.dependencies import (
    CreateShortURLUseCaseDependency,
    make_create_shorturl_use_case,
    make_sqlalchemy_user_repository,
    make_sqlalchemy_shorturl_repository
)

from tests.utils.type_helpers import get_annotated_args


@pytest.fixture
def use_case():
    return make_create_shorturl_use_case()


def test_instance(use_case: CreateShortURLUseCase):
    assert isinstance(use_case, CreateShortURLUseCase)


def test_dependency():
    args = get_annotated_args(CreateShortURLUseCaseDependency)
    assert args[0] == CreateShortURLUseCase
    assert isinstance(args[1], Depends)
    assert args[1].dependency == make_create_shorturl_use_case


def test_attr_shorturl_repository(use_case: CreateShortURLUseCase):
    assert isinstance(use_case.shorturl_repository, Depends)
    assert (
        use_case.shorturl_repository.dependency == 
        make_sqlalchemy_shorturl_repository
    )


def test_attr_user_repository(use_case: CreateShortURLUseCase):
    assert isinstance(use_case.user_repository, Depends)
    assert (
        use_case.user_repository.dependency == make_sqlalchemy_user_repository
    )
