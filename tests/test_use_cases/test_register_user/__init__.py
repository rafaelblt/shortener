import pytest

from datetime import timedelta

from shortener.domain.plan import Plan
from shortener.domain.plan.exceptions import PlanNotFoundError

from shortener.domain.services.email_template import EmailTemplate
from shortener.domain.shared.email import Email
from shortener.domain.shared.primarykey import PrimaryKey
from shortener.domain.shared.language import Language
from shortener.domain.shared.exceptions import ValidationError, MultiValidationError
from shortener.domain.shared.validator import Validator

from shortener.domain.user import User
from shortener.domain.user.fields import Name, PlainPassword, UserStatus, HashedPassword
from shortener.domain.user.exceptions import EmailAlreadyExistsError

from shortener.use_cases import RegisterUserUseCase

from tests.fixtures.mocks import MockSendEmailService, MockAuthTokenService


@pytest.fixture
def plain_password():
    return PlainPassword("T!@#jnmuj1GBals*#71")


@pytest.fixture
def use_case(
    mock_user_repository,
    mock_plan_repository,
    mock_password_hasher,
    mock_send_email_service,
    mock_email_template,
):
    token_service = MockAuthTokenService(
        purpose="email_verification",
        expires_in=timedelta(minutes=60),
        user_repository=mock_user_repository
    )
    return RegisterUserUseCase(
        user_repository=mock_user_repository,
        plan_repository=mock_plan_repository,
        token_service=token_service,
        send_email_service=mock_send_email_service,
        password_hasher=mock_password_hasher,
        email_template=mock_email_template,
    )
