import os
import pytest

from unittest.mock import patch

from fastapi.params import Depends

from shortener.infra.dependencies.fastapi.services.password_hasher import (
    make_passlib_password_hasher_service,
    get_password_hasher_service,
)
from shortener.infra.services.passlib_hasher import PasslibPasswordHasher
from shortener.infra.settings import reload_settings


def test_make_passlib_password_hasher_service():
    retrieved = make_passlib_password_hasher_service()
    assert isinstance(retrieved, PasslibPasswordHasher)


@pytest.mark.parametrize(
    ["impl", "expected_dependency"],
    [
        ("passlib", make_passlib_password_hasher_service),
        ("", make_passlib_password_hasher_service),
    ]
)
def test_get_dependency_impl(impl, expected_dependency):
    with patch.dict(os.environ):
        os.environ["PASSWORD_HASHER_SERVICE_IMPL"] = impl
        reload_settings()
        retrieved = get_password_hasher_service()
        assert isinstance(retrieved, Depends)
        assert retrieved.dependency == expected_dependency
