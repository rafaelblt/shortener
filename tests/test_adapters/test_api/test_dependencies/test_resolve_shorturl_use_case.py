import pytest

from fastapi.params import Depends

from shortener.domain.shorturl.validators import AvailabilityValidator

from shortener.use_cases import ResolveShortURLUseCase

from shortener.adapters.api.dependencies import (
    make_resolve_shorturl_use_case, make_sqlalchemy_shorturl_repository
)


@pytest.fixture
def use_case():
    return make_resolve_shorturl_use_case()


def test_instance(use_case: ResolveShortURLUseCase):
    assert isinstance(use_case, ResolveShortURLUseCase)


def test_attr_repository(use_case: ResolveShortURLUseCase):
    assert isinstance(use_case.repository, Depends)
    assert use_case.repository.dependency == make_sqlalchemy_shorturl_repository


def test_attr_validator(use_case: ResolveShortURLUseCase):
    assert isinstance(use_case.validator, AvailabilityValidator)
