import pytest

from tests.fixtures import MockSendEmailService, MockAuthTokenService

from shortener.domain.shared.validator import Validator
from shortener.domain.shared.exceptions import ValidationError

from shortener.domain.services.password_validator import PasswordValidatorService
from shortener.domain.services.email_template_renderer import EmailTemplateRenderer
from shortener.domain.services.exceptions import PasswordValidationError

from shortener.domain.plan import Plan
from shortener.domain.plan.exceptions import PlanNotFoundInDatabaseError

from shortener.domain.user import User
from shortener.domain.user.fields import Email, Name, UserStatus

from shortener.use_cases.register_user import RegisterUserUseCase


class MockEmailValidator(Validator):
    async def validate(self, value: Email):
        if value == "joker@gmail.com":
            raise ValidationError("email validation error")


class MockNameValidator(Validator):
    async def validate(self, value: Name):
        if value == "Joker":
            raise ValidationError("name validation error")
        

class MockEmailTemplateRenderer(EmailTemplateRenderer):
    def render_subject(self, **kwargs) -> str:
        return "Verification Email"

    def render_body(self, **kwargs) -> str:
        token = kwargs.pop("token")
        name = kwargs.pop("name")
        expires_minutes = kwargs.pop("expires_minutes")
        return f"Token: {token}, name: {name}, expires_minutes: {expires_minutes}"


@pytest.fixture
def use_case(
    mock_user_repository,
    mock_plan_repository,
    mock_password_hasher,
    mock_auth_token_service,
    mock_send_email_service
):
    return RegisterUserUseCase(
        user_repository=mock_user_repository,
        plan_repository=mock_plan_repository,
        auth_token_service=mock_auth_token_service,
        send_email_service=mock_send_email_service,
        password_hasher=mock_password_hasher,
        email_template_renderer=MockEmailTemplateRenderer(),
        validators={
            "email": [MockEmailValidator()],
            "name": [MockNameValidator()],
            "password": [PasswordValidatorService()]
        }
    )


@pytest.mark.asyncio
async def test_instance_retrieved(
    use_case: RegisterUserUseCase, normal_user: User, default_plan: Plan
):
    plan = await use_case.plan_repository.add(default_plan)

    plain_password = "T!@#jnmuj1GBals*#71"

    retrieved = await use_case.execute(
        email=normal_user.email, 
        name=normal_user.name, 
        plan_id=plan.get_int_id(),
        password=plain_password
    )

    assert isinstance(retrieved, User)
    assert retrieved.email == normal_user.email
    assert retrieved.name == normal_user.name
    assert retrieved.plan.id == plan.id
    assert retrieved.status == UserStatus.UNVERIFIED_EMAIL
    assert use_case.password_hasher.verify(
        plain_password, retrieved.hashed_password
    )


@pytest.mark.asyncio
async def test_raises_plan_not_found(
    use_case: RegisterUserUseCase, normal_user: User
):
    with pytest.raises(PlanNotFoundInDatabaseError) as error:
        await use_case.execute(
            email=normal_user.email, 
            name=normal_user.name, 
            plan_id=1,
            password="Test123#"
        )
    assert error.value.plan_id == 1


@pytest.mark.asyncio
async def test_raises_email_validation_error(
    use_case: RegisterUserUseCase, normal_user: User, default_plan: Plan
):
    plan = await use_case.plan_repository.add(default_plan)

    joker_email = Email("joker@gmail.com")
    with pytest.raises(ValidationError, match="email validation error"):
        await use_case.execute(
            email=joker_email, 
            name=normal_user.name, 
            plan_id=plan.get_int_id(),
            password="Test123#"
        )


@pytest.mark.asyncio
async def test_raises_name_validation_error(
    use_case: RegisterUserUseCase, normal_user: User, default_plan: Plan
):
    plan = await use_case.plan_repository.add(default_plan)

    joker_name = Name("Joker")
    with pytest.raises(ValidationError, match="name validation error"):
        await use_case.execute(
            email=normal_user.email, 
            name=joker_name, 
            plan_id=plan.get_int_id(),
            password="Test123#"
        )


@pytest.mark.asyncio
async def test_raises_password_validation_error(
    use_case: RegisterUserUseCase, normal_user: User, default_plan: Plan
):
    plan = await use_case.plan_repository.add(default_plan)

    with pytest.raises(PasswordValidationError):
        await use_case.execute(
            email=normal_user.email, 
            name=normal_user.name, 
            plan_id=plan.get_int_id(),
            password="123"
        )


@pytest.mark.asyncio
async def test_if_user_is_saved_in_repository(
    use_case: RegisterUserUseCase, normal_user: User, default_plan: Plan
):
    plan = await use_case.plan_repository.add(default_plan)
    await use_case.execute(
        email=normal_user.email, 
        name=normal_user.name, 
        plan_id=plan.get_int_id(),
        password="T!@#jnmuj1GBals*#71"
    )
    assert await use_case.user_repository.exists_by_email(normal_user.email)


@pytest.mark.asyncio
async def test_if_email_is_sent_with_token(
    use_case: RegisterUserUseCase, normal_user: User, default_plan: Plan
):
    plan = await use_case.plan_repository.add(default_plan)
    await use_case.execute(
        email=normal_user.email, 
        name=normal_user.name, 
        plan_id=plan.get_int_id(),
        password="T!@#jnmuj1GBals*#71"
    )

    assert isinstance(use_case.send_email_service, MockSendEmailService)
    assert isinstance(use_case.auth_token_service, MockAuthTokenService)
    
    template = MockEmailTemplateRenderer()
    token = use_case.auth_token_service.mock_data["generated_tokens"][0]
    expires_minutes = use_case.auth_token_service.expires_minutes
    
    email_log = use_case.send_email_service.mock_logs[0]
    assert email_log["receiver"] == normal_user.email
    assert email_log["subject"] == template.render_subject()
    assert email_log["body"] == template.render_body(
        token=token, expires_minutes=expires_minutes, name=normal_user.name
    )
