import pytest

from pydantic import BaseModel

from shortener.adapters.api.v1.schemas.auth import LoginResponse


@pytest.fixture
def schema():
    return LoginResponse(
        access_token="token",
        token_type="bearer",
        expires_minutes=1,
        email="test-email"
    )


def test_inheritance_base_model(schema: LoginResponse):
    assert isinstance(schema, BaseModel)


def test_attr_access_token(schema: LoginResponse):
    assert isinstance(schema.access_token, str)
    

def test_attr_token_type(schema: LoginResponse):
    assert isinstance(schema.token_type, str)


def test_attr_expires_minutes(schema: LoginResponse):
    assert isinstance(schema.expires_minutes, int)


def test_attr_email(schema: LoginResponse):
    assert isinstance(schema.email, str)
