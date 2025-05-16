import pytest

from shortener.domain.services.password_validator import PasswordValidatorService
from shortener.domain.services.exceptions import PasswordValidationError

from shortener.domain.plan import Plan
from shortener.domain.plan.exceptions import PlanNotFoundInDatabaseError

from shortener.domain.user import User, UserValidator
from shortener.domain.user.fields import Email
from shortener.domain.user.exceptions import UserValidationError

from shortener.use_cases.create_user import CreateUserUseCase


class MockUserValidator(UserValidator):
    async def validate(self, user: User):
        if user.email == "joker@gmail.com":
            raise UserValidationError()


@pytest.fixture
def use_case(
    mock_user_repository,
    mock_plan_repository,
    mock_password_hasher
):
    return CreateUserUseCase(
        user_repository=mock_user_repository,
        plan_repository=mock_plan_repository,
        password_hasher=mock_password_hasher,
        password_validator=PasswordValidatorService(),
        user_validator=MockUserValidator(),
    )


@pytest.mark.asyncio
async def test_instance_retrieved(
    use_case: CreateUserUseCase, normal_user: User, default_plan: Plan
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
    assert use_case.password_hasher.verify(
        plain_password, retrieved.hashed_password
    )


@pytest.mark.asyncio
async def test_raises_plan_not_found(
    use_case: CreateUserUseCase, normal_user: User
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
async def test_raises_password_validation(
    use_case: CreateUserUseCase, normal_user: User, default_plan: Plan
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
async def test_raises_user_validation(
    use_case: CreateUserUseCase, normal_user: User, default_plan: Plan
):
    plan = await use_case.plan_repository.add(default_plan)

    joker_email = Email("joker@gmail.com")
    with pytest.raises(UserValidationError):
        await use_case.execute(
            email=joker_email, 
            name=normal_user.name, 
            plan_id=plan.get_int_id(),
            password="Test123#"
        )


@pytest.mark.asyncio
async def test_if_user_is_saved_in_repository(
    use_case: CreateUserUseCase, normal_user: User, default_plan: Plan
):
    plan = await use_case.plan_repository.add(default_plan)
    await use_case.execute(
        email=normal_user.email, 
        name=normal_user.name, 
        plan_id=plan.get_int_id(),
        password="T!@#jnmuj1GBals*#71"
    )
    assert await use_case.user_repository.exists_by_email(normal_user.email)
