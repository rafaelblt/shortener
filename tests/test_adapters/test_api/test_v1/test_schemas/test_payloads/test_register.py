import pytest

from pydantic import BaseModel, ValidationError

from shortener.adapters.api.v1.schemas.payloads.auth import RegisterPayload

from shortener.domain.shared.exceptions import EmailInvalidError
from shortener.domain.shared.primarykey import PrimaryKey
from shortener.domain.user import User
from shortener.domain.user.exceptions import NameTooShortError, PasswordMissingSpecialCharError
from shortener.domain.user.fields import Email, Name, PlainPassword

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
    return RegisterPayload(
        email=valid_email,
        name=valid_name,
        password=valid_password,
        plan_id=1
    )


def test_inheritance_base_model(schema: RegisterPayload):
    assert isinstance(schema, BaseModel)


def test_attr_email(schema: RegisterPayload):
    assert isinstance(schema.email, str)


def test_attr_name(schema: RegisterPayload):
    assert isinstance(schema.name, str)


def test_attr_password(schema: RegisterPayload):
    assert isinstance(schema.password, str)


def test_attr_plan_id(schema: RegisterPayload):
    assert isinstance(schema.plan_id, int)


def test_email_after_validator(valid_name: str, valid_password: str):
    with pytest.raises(ValidationError) as error:
        RegisterPayload(
            email="invalid_email",
            name=valid_name,
            password=valid_password,
            plan_id=1
        )
    assert error.value.errors()[0]["type"] == EmailInvalidError.code


def test_name_after_validator(valid_email: str, valid_password: str):
    with pytest.raises(ValidationError) as error:
        RegisterPayload(
            email=valid_email,
            name="a",
            password=valid_password,
            plan_id=1
        )
    assert error.value.errors()[0]["type"] == NameTooShortError.code


def test_password_after_validator(valid_email: str, valid_name: str):
    with pytest.raises(ValidationError) as error:
        RegisterPayload(
            email=valid_email,
            name=valid_name,
            password="aA1bB2cC3dD4eEfF5",
            plan_id=1
        )
    assert error.value.errors()[0]["type"] == PasswordMissingSpecialCharError.code


def test_method_get_email(schema: RegisterPayload, valid_email: str):
    retrieved = schema.get_email()
    assert isinstance(retrieved, Email)
    assert retrieved == valid_email


def test_method_get_name(schema: RegisterPayload, valid_name: str):
    retrieved = schema.get_name()
    assert isinstance(retrieved, Name)
    assert retrieved == valid_name


def test_method_get_password(schema: RegisterPayload, valid_password: str):
    retrieved = schema.get_password()
    assert isinstance(retrieved, PlainPassword)
    assert retrieved == valid_password


def test_method_get_plan_pk(schema: RegisterPayload):
    retrieved = schema.get_plan_pk()
    assert isinstance(retrieved, PrimaryKey)
    assert retrieved.get_id() == 1
