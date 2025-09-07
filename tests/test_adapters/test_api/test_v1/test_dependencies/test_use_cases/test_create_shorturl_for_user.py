import pytest

from fastapi.params import Depends

from shortener.use_cases import CreateShortURLForUserUseCase

from shortener.adapters.api.v1.dependencies import (
    CreateShortURLForUserUseCaseDependency,
    make_create_shorturl_for_user_use_case,
    make_sqlalchemy_shorturl_repository
)

from tests.utils.type_helpers import get_annotated_args


@pytest.fixture
def use_case():
    return make_create_shorturl_for_user_use_case()


def test_instance(use_case: CreateShortURLForUserUseCase):
    assert isinstance(use_case, CreateShortURLForUserUseCase)


def test_dependency():
    args = get_annotated_args(CreateShortURLForUserUseCaseDependency)
    assert args[0] == CreateShortURLForUserUseCase
    assert isinstance(args[1], Depends)
    assert args[1].dependency == make_create_shorturl_for_user_use_case


def test_attr_shorturl_repository(use_case: CreateShortURLForUserUseCase):
    assert isinstance(use_case.shorturl_repository, Depends)
    assert (
        use_case.shorturl_repository.dependency == 
        make_sqlalchemy_shorturl_repository
    )
