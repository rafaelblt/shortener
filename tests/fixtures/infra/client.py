import pytest

from fastapi.testclient import TestClient
from shortener.infra.db import get_session

from shortener.adapters.api import app


@pytest.fixture
def client(db_session):

    def session_override():
        return db_session

    with TestClient(app) as client:
        app.dependency_overrides[get_session] = session_override
        yield client

    app.dependency_overrides.clear()
