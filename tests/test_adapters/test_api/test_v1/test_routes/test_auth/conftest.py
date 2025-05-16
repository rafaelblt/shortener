import pytest

from shortener.adapters.api.v1.routes.auth import router


@pytest.fixture
def route():
    return router.prefix
