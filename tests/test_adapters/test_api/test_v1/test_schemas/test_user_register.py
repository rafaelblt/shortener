import pytest

from pydantic import ValidationError

from shortener.domain.user import User
from shortener.domain.user.fields import Email, Name
from shortener.domain.user.fields.name import NAME_MIN_LENGTH

from shortener.adapters.api.v1.schemas import UserRegisterSchema


@pytest.fixture
def valid_email(normal_user: User):
    return str(normal_user.email)

@pytest.fixture
def valid_name(normal_user: User):
    return str(normal_user.name)

@pytest.fixture
def valid_schema(valid_email: str, valid_name: str):
    return UserRegisterSchema(
        email=valid_email,
        name=valid_name,
        password="pass123",
        plan_id=1
    )


def test_valid_data(valid_email:str, valid_name: str):
    UserRegisterSchema(
        email=valid_email,
        name=valid_name,
        password="pass123",
        plan_id=1
    )


def test_raises_validation_error_without_data():
    with pytest.raises(ValidationError) as error:
        UserRegisterSchema()

    assert error.value.error_count() == 4

    errors = error.value.errors()
    actual_fields = {e['loc'][0] for e in errors}
    expected_fields = {"email", "name", "password", "plan_id"}

    assert actual_fields == expected_fields
    for err in errors:
        assert err["type"] == "missing"


def test_email_after_validator(valid_name: str):
    with pytest.raises(ValidationError) as error:
        UserRegisterSchema(
            email="invalid_email",
            name=valid_name,
            password="pass123",
            plan_id=1
        )
    assert error.value.errors()[0]["type"] == "invalid_email"


def test_name_after_validator(valid_email: str):
    with pytest.raises(ValidationError) as error:
        UserRegisterSchema(
            email=valid_email,
            name="a",
            password="pass123",
            plan_id=1
        )
    assert error.value.errors()[0]["type"] == "invalid_name"


def test_method_get_email(valid_schema: UserRegisterSchema, valid_email: str):
    retrieved = valid_schema.get_email()
    assert isinstance(retrieved, Email)
    assert retrieved == valid_email


def test_method_get_name(valid_schema: UserRegisterSchema, valid_name: str):
    retrieved = valid_schema.get_name()
    assert isinstance(retrieved, Name)
    assert retrieved == valid_name


def test_json_schema_example(valid_schema: UserRegisterSchema):
    example = valid_schema.model_json_schema()["example"]
    assert example == {
        "email": "user@example.com",
        "name": "User Name Example",
        "password": "Pass123",
        "plan_id": 1
    }
