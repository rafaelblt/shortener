import pytest

from tests.utils.entity_helpers import get_persistent_plan

from shortener.domain.services.password_hasher import PasswordHasher

from shortener.domain.plan import Plan, PlanRepository

from shortener.domain.user import User, UserRepository, UserValidator
from shortener.domain.user.fields import Email
from shortener.domain.user.exceptions import UserValidationError

from shortener.use_cases.create_user import CreateUserUseCase


class MockPasswordHasher(PasswordHasher):
    def hash(self, plain_password: str) -> str:
        return f"hashed-{plain_password}"

    def verify(self, plain_password: str, hashed_password: str) -> bool:
        return hashed_password == f"hashed-{plain_password}"


class MockValidator(UserValidator):
    async def validate(self, user: User):
        if user.email == "joker@gmail.com":
            raise UserValidationError()


@pytest.fixture
def use_case(mock_user_repository, mock_plan_repository):
    return CreateUserUseCase(
        user_repository=mock_user_repository,
        plan_repository=mock_plan_repository,
        password_hasher=MockPasswordHasher(),
        validator=MockValidator(),
    )


@pytest.mark.asyncio
async def test_instance_retrieved(
    use_case: CreateUserUseCase, normal_user: User, default_plan: Plan
):
    plan = await use_case.plan_repository.add(default_plan)

    retrieved = await use_case.execute(
        email=normal_user.email, 
        name=normal_user.name, 
        plan_id=plan.id,
        password="Test123#"
    )

    assert isinstance(retrieved, User)
    assert retrieved.email == normal_user.email
    assert retrieved.name == normal_user.name
    assert retrieved.plan.id == plan.id
    assert use_case.password_hasher.verify("Test123#", retrieved.hashed_password)


@pytest.mark.asyncio
async def test_with_non_existent_plan(
    use_case: CreateUserUseCase, normal_user: User
):
    with pytest.raises(
        UserValidationError, 
        match="There is no plan in the database with the given plan_id: 1."
    ):
        await use_case.execute(
            email=normal_user.email, 
            name=normal_user.name, 
            plan_id=1,
            password="Test123#"
        )


@pytest.mark.asyncio
async def test_raises_validation(
    use_case: CreateUserUseCase, normal_user: User, default_plan: Plan
):
    plan = await use_case.plan_repository.add(default_plan)
    joker_email = Email("joker@gmail.com")
    with pytest.raises(UserValidationError):
        await use_case.execute(
            email=joker_email, 
            name=normal_user.name, 
            plan_id=plan.id,
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
        plan_id=plan.id,
        password="Test123#"
    )
    assert await use_case.user_repository.exists_by_email(normal_user.email)
