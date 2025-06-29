import pytest

from fastapi.testclient import TestClient
from shortener.adapters.api import app


@pytest.fixture
def client(dependency_overrides: dict):

    with TestClient(app) as client:
        for dependency, override in dependency_overrides.items():
            app.dependency_overrides[dependency] = override
        yield client

    app.dependency_overrides.clear()
