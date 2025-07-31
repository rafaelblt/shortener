import pytest

from pydantic import BaseModel, ValidationError

from shortener.domain.shared.exceptions import EmailInvalidError
from shortener.domain.shared.primarykey import PrimaryKey
from shortener.domain.user import User
from shortener.domain.user.exceptions import NameTooShortError, PasswordMissingSpecialCharError
from shortener.domain.user.fields import Email, Name

from shortener.adapters.api.v1.schemas.requests.auth import RegisterRequest
from shortener.domain.user.fields.plain_password import PlainPassword
from tests.fixtures.domain.users import UserFixture


@pytest.fixture
def valid_email(normal_user: User):
    return str(normal_user.email)

@pytest.fixture
def valid_name(normal_user: User):
    return str(normal_user.name)

@pytest.fixture
def valid_password(normal_user: UserFixture):
    return str(normal_user.mock_data["plain_password"])

@pytest.fixture
def schema(valid_email: str, valid_name: str, valid_password: str):
    return RegisterRequest(
        email=valid_email,
        name=valid_name,
        password=valid_password,
        plan_id=1
    )


def test_inheritance_base_model(schema: RegisterRequest):
    assert isinstance(schema, BaseModel)


def test_attr_email(schema: RegisterRequest):
    assert isinstance(schema.email, str)


def test_attr_name(schema: RegisterRequest):
    assert isinstance(schema.name, str)


def test_attr_password(schema: RegisterRequest):
    assert isinstance(schema.password, str)


def test_attr_plan_id(schema: RegisterRequest):
    assert isinstance(schema.plan_id, int)


def test_email_after_validator(valid_name: str, valid_password: str):
    with pytest.raises(ValidationError) as error:
        RegisterRequest(
            email="invalid_email",
            name=valid_name,
            password=valid_password,
            plan_id=1
        )
    assert error.value.errors()[0]["type"] == EmailInvalidError.code


def test_name_after_validator(valid_email: str, valid_password: str):
    with pytest.raises(ValidationError) as error:
        RegisterRequest(
            email=valid_email,
            name="a",
            password=valid_password,
            plan_id=1
        )
    assert error.value.errors()[0]["type"] == NameTooShortError.code


def test_password_after_validator(valid_email: str, valid_name: str):
    with pytest.raises(ValidationError) as error:
        RegisterRequest(
            email=valid_email,
            name=valid_name,
            password="aA1bB2cC3dD4eEfF5",
            plan_id=1
        )
    assert error.value.errors()[0]["type"] == PasswordMissingSpecialCharError.code


def test_method_get_email(schema: RegisterRequest, valid_email: str):
    retrieved = schema.get_email()
    assert isinstance(retrieved, Email)
    assert retrieved == valid_email


def test_method_get_name(schema: RegisterRequest, valid_name: str):
    retrieved = schema.get_name()
    assert isinstance(retrieved, Name)
    assert retrieved == valid_name


def test_method_get_password(schema: RegisterRequest, valid_password: str):
    retrieved = schema.get_password()
    assert isinstance(retrieved, PlainPassword)
    assert retrieved == valid_password


def test_method_get_plan_pk(schema: RegisterRequest):
    retrieved = schema.get_plan_pk()
    assert isinstance(retrieved, PrimaryKey)
    assert retrieved.get_id() == 1


def test_json_schema_example(schema: RegisterRequest):
    example = schema.model_json_schema()["example"]
    assert example == {
        "email": "user@example.com",
        "name": "User Name Example",
        "password": "Pass@123",
        "plan_id": 1
    }
