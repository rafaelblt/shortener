from . import *


@pytest.mark.asyncio
async def test_raises_email_validation_error(
    use_case: RegisterUserUseCase,
    normal_user: User,
    default_plan: Plan,
    plain_password: PlainPassword
):
    plan = await use_case.plan_repository.add(default_plan)
    joker_email = Email("joker@gmail.com")
    with pytest.raises(MultiValidationError) as error:
        await use_case.execute(
            email=joker_email, 
            name=normal_user.name, 
            plan_id=plan.get_int_id(),
            password=plain_password,
            lang=Language.EN
        )
    assert error.value.errors[0].code == "EMAIL_ERROR"


@pytest.mark.asyncio
async def test_raises_name_validation_error(
    use_case: RegisterUserUseCase,
    normal_user: User,
    default_plan: Plan,
    plain_password: PlainPassword
):
    plan = await use_case.plan_repository.add(default_plan)
    joker_name = Name("Joker")
    with pytest.raises(MultiValidationError) as error:
        await use_case.execute(
            email=normal_user.email, 
            name=joker_name, 
            plan_id=plan.get_int_id(),
            password=plain_password,
            lang=Language.EN
        )
    assert error.value.errors[0].code == "NAME_ERROR"


@pytest.mark.asyncio
async def test_raises_password_validation_error(
    use_case: RegisterUserUseCase,
    normal_user: User
):
    joker_pwd = PlainPassword("Joker@#@123")
    with pytest.raises(MultiValidationError) as error:
        await use_case.execute(
            email=normal_user.email, 
            name=normal_user.name, 
            plan_id=1,
            password=joker_pwd,
            lang=Language.EN
        )
    assert error.value.errors[0].code == "PASSWORD_ERROR"


@pytest.mark.asyncio
async def test_raises_plan_id_validation_error(
    use_case: RegisterUserUseCase, normal_user: User, plain_password: PlainPassword
):
    with pytest.raises(MultiValidationError) as error:
        await use_case.execute(
            email=normal_user.email, 
            name=normal_user.name, 
            plan_id=0,
            password=plain_password,
            lang=Language.EN
        )
    assert error.value.errors[0].code == "PLAN_ID_ERROR"
