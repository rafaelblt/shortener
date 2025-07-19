from . import *


@pytest.mark.asyncio
async def test_raises_plan_not_found(
    use_case: RegisterUserUseCase, normal_user: User, plain_password: PlainPassword
):
    with pytest.raises(PlanNotFoundError) as error:
        await use_case.execute(
            email=normal_user.email, 
            name=normal_user.name, 
            plan_id=1,
            password=plain_password,
            lang=Language.EN
        )
    assert error.value.plan_id == 1


@pytest.mark.asyncio
async def test_raises_email_already_exists(
    use_case: RegisterUserUseCase,
    normal_user: User,
    default_plan: Plan,
    plain_password: PlainPassword
):
    plan = await use_case.plan_repository.add(default_plan)

    await use_case.execute(
        email=normal_user.email, 
        name=normal_user.name, 
        plan_id=plan.get_int_id(),
        password=plain_password,
        lang=Language.EN
    )

    with pytest.raises(EmailAlreadyExistsError) as error:
        await use_case.execute(
            email=normal_user.email, 
            name=normal_user.name, 
            plan_id=1,
            password=plain_password,
            lang=Language.EN
        )
    
    assert error.value.value == normal_user.email
