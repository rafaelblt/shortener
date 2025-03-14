import pytest
from http import HTTPStatus as HTTPStatusLib


@pytest.fixture
def HTTPStatus():
    return HTTPStatusLib
