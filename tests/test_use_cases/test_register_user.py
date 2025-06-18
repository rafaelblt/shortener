import pytest

from tests.fixtures import MockSendEmailService, MockAuthTokenService

from shortener.domain.shared.language import Language
from shortener.domain.shared.validator import Validator
from shortener.domain.shared.exceptions import ValidationError

from shortener.domain.services.password_validator import PasswordValidatorService
from shortener.domain.services.email_template import EmailTemplate
from shortener.domain.services.exceptions import PasswordValidationError

from shortener.domain.plan import Plan
from shortener.domain.plan.exceptions import PlanNotFoundError

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
        

class MockEmailTemplate(EmailTemplate):
    REQUIRED_CONTEXT_VARS = ["token", "user_name", "expires_minutes"]

    def render_subject(self, lang: Language, context: dict[str, str]) -> str:
        return f"{lang} => Verification Email"

    def render_plain_body(self, lang: Language, context: dict[str, str]) -> str:
        ctx = self.process_context(context)
        token = ctx["token"]
        user_name = ctx["user_name"]
        expires_minutes = ctx["expires_minutes"]
        return f"{token} // {user_name} // {expires_minutes} // {lang}"
    
    def render_html_body(self, lang: Language, context: dict[str, str]) -> str:
        ctx = self.process_context(context)
        token = ctx["token"]
        user_name = ctx["user_name"]
        expires_minutes = ctx["expires_minutes"]
        return f"<html>{token} : {user_name} : {expires_minutes} : {lang}</html>"


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
        email_template=MockEmailTemplate(),
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
        password=plain_password,
        lang=Language.EN
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
    with pytest.raises(PlanNotFoundError) as error:
        await use_case.execute(
            email=normal_user.email, 
            name=normal_user.name, 
            plan_id=1,
            password="Test123#",
            lang=Language.EN
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
            password="Test123#",
            lang=Language.EN
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
            password="Test123#",
            lang=Language.EN
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
            password="123",
            lang=Language.EN
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
        password="T!@#jnmuj1GBals*#71",
        lang=Language.EN
    )
    assert await use_case.user_repository.exists_by_email(normal_user.email)


@pytest.mark.asyncio
async def test_if_email_is_sent_with_token(
    use_case: RegisterUserUseCase, normal_user: User, default_plan: Plan
):
    example_lang = Language.PT_BR
    plan = await use_case.plan_repository.add(default_plan)
    await use_case.execute(
        email=normal_user.email, 
        name=normal_user.name, 
        plan_id=plan.get_int_id(),
        password="T!@#jnmuj1GBals*#71",
        lang=example_lang
    )

    assert isinstance(use_case.auth_token_service, MockAuthTokenService)
    expected_context = {
        "token": use_case.auth_token_service.mock_data["generated_tokens"][0],
        "expires_minutes": use_case.auth_token_service.expires_minutes,
        "user_name": normal_user.name
    }

    template = MockEmailTemplate()
    expected_email_log = {
        "to": normal_user.email,
        "subject": template.render_subject(example_lang, expected_context),
        "plain_body": template.render_plain_body(example_lang, expected_context),
        "html_body": template.render_html_body(example_lang, expected_context)
    }
    
    assert isinstance(use_case.send_email_service, MockSendEmailService)
    email_log = use_case.send_email_service.mock_logs[0]
    assert email_log == expected_email_log
