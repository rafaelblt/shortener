import pytest

from fastapi.params import Depends

from shortener.domain.shorturl import SlugGenerator
from shortener.domain.shorturl.validators import GeneralValidator

from shortener.use_cases import CreateShortURLUseCase

from shortener.adapters.api.v1.dependencies import (
    make_create_shorturl_use_case, make_sqlalchemy_shorturl_repository
)


@pytest.fixture
def use_case():
    return make_create_shorturl_use_case()


def test_instance(use_case: CreateShortURLUseCase):
    assert isinstance(use_case, CreateShortURLUseCase)


def test_attr_repository(use_case: CreateShortURLUseCase):
    assert isinstance(use_case.repository, Depends)
    assert use_case.repository.dependency == make_sqlalchemy_shorturl_repository


def test_attr_validator(use_case: CreateShortURLUseCase):
    assert isinstance(use_case.validator, GeneralValidator)


def test_attr_slug_generator(use_case: CreateShortURLUseCase):
    assert isinstance(use_case.slug_generator, SlugGenerator)
