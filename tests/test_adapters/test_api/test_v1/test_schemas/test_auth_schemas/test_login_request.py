import pytest

from pydantic import BaseModel, ValidationError

from shortener.domain.user.fields import Email
from shortener.adapters.api.v1.schemas.requests.auth import LoginRequest


@pytest.fixture
def valid_email(normal_user):
    return str(normal_user.email)

@pytest.fixture
def schema(valid_email):
    return LoginRequest(
        email=valid_email,
        password="pass123"
    )


def test_inheritance_base_model(schema: LoginRequest):
    assert isinstance(schema, BaseModel)


def test_attr_email(schema: LoginRequest):
    assert isinstance(schema.email, str)


def test_attr_password(schema: LoginRequest):
    assert isinstance(schema.password, str)


def test_method_get_email(schema: LoginRequest, valid_email: str):
    retrieved = schema.get_email()
    assert isinstance(retrieved, Email)
    assert retrieved == valid_email


def test_email_after_validator():
    with pytest.raises(ValidationError) as error:
        LoginRequest(email="invalid_email", password="123")
    assert error.value.errors()[0]["type"] == "invalid_email"


def test_json_schema_example(schema: LoginRequest):
    example = schema.model_json_schema()["example"]
    assert example == {
        "email": "user@example.com",
        "password": "pass123"
    }
