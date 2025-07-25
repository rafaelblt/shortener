from datetime import timedelta
import pytest

from shortener.domain.plan import Plan
from shortener.domain.plan.exceptions import PlanNotFoundError

from shortener.domain.services.email_template import EmailTemplate
from shortener.domain.shared.email import Email
from shortener.domain.shared.language import Language
from shortener.domain.shared.exceptions import ValidationError, MultiValidationError
from shortener.domain.shared.validator import Validator

from shortener.domain.user import User
from shortener.domain.user.fields import Name, PlainPassword, UserStatus, HashedPassword
from shortener.domain.user.exceptions import EmailAlreadyExistsError

from shortener.use_cases import RegisterUserUseCase

from tests.fixtures import MockSendEmailService, MockTokenService


class MockEmailValidator(Validator):
    async def validate(self, value: Email):
        if value == "joker@gmail.com":
            raise ValidationError(value, "email", "EMAIL_ERROR", "error message")


class MockNameValidator(Validator):
    async def validate(self, value: Name):
        if value == "Joker":
            raise ValidationError(value, "name", "NAME_ERROR", "error message")
        

class MockPasswordValidator(Validator):
    async def validate(self, value: PlainPassword):
        if "Joker" in value:
            raise ValidationError(value, "paswsord", "PASSWORD_ERROR", "error message")
        

class MockPlanIdValidator(Validator):
    async def validate(self, value: int):
        if value == 0:
            raise ValidationError(value, "paswsord", "PLAN_ID_ERROR", "error message")


@pytest.fixture
def plain_password():
    return PlainPassword("T!@#jnmuj1GBals*#71")


EMAIL_VERIFICATION_EXPIRES_IN = timedelta(minutes=60)


@pytest.fixture
def use_case(
    mock_user_repository,
    mock_plan_repository,
    mock_password_hasher,
    mock_token_service,
    mock_send_email_service,
    mock_email_template,
):
    return RegisterUserUseCase(
        user_repository=mock_user_repository,
        plan_repository=mock_plan_repository,
        token_service=mock_token_service,
        send_email_service=mock_send_email_service,
        password_hasher=mock_password_hasher,
        email_template=mock_email_template,
        email_verification_expires_in=EMAIL_VERIFICATION_EXPIRES_IN,
        validators_map={
            "email": [MockEmailValidator()],
            "name": [MockNameValidator()],
            "password": [MockPasswordValidator()],
            "plan_id": [MockPlanIdValidator()]
        }
    )
