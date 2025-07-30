from . import *


@pytest.mark.asyncio
async def test_instance_retrieved(
    use_case: RegisterUserUseCase,
    normal_user: User,
    default_plan: Plan,
    plain_password: PlainPassword
):
    plan = await use_case.plan_repository.add(default_plan)

    retrieved = await use_case.execute(
        email=normal_user.email, 
        name=normal_user.name, 
        plan_pk=plan.pk,
        password=plain_password,
        lang=Language.EN
    )

    assert isinstance(retrieved, User)


@pytest.mark.asyncio
async def test_created_user_attributes(
    use_case: RegisterUserUseCase,
    normal_user: User,
    default_plan: Plan,
    plain_password: PlainPassword
):
    plan = await use_case.plan_repository.add(default_plan)

    user = await use_case.execute(
        email=normal_user.email, 
        name=normal_user.name, 
        plan_pk=plan.pk,
        password=plain_password,
        lang=Language.EN
    )

    assert user.email == normal_user.email
    assert user.name == normal_user.name
    assert user.plan.pk == plan.pk
    assert user.status == UserStatus.UNVERIFIED_EMAIL
    assert isinstance(user.hashed_password, HashedPassword)


@pytest.mark.asyncio
async def test_hashed_password(
    use_case: RegisterUserUseCase,
    normal_user: User,
    default_plan: Plan,
    plain_password: PlainPassword
):
    plan = await use_case.plan_repository.add(default_plan)

    user = await use_case.execute(
        email=normal_user.email, 
        name=normal_user.name, 
        plan_pk=plan.pk,
        password=plain_password,
        lang=Language.EN
    )

    assert use_case.password_hasher.verify(plain_password, user.hashed_password)


@pytest.mark.asyncio
async def test_if_user_is_saved_in_repository(
    use_case: RegisterUserUseCase,
    normal_user: User,
    default_plan: Plan,
    plain_password: PlainPassword
):
    plan = await use_case.plan_repository.add(default_plan)

    await use_case.execute(
        email=normal_user.email, 
        name=normal_user.name, 
        plan_pk=plan.pk,
        password=plain_password,
        lang=Language.EN
    )

    assert await use_case.user_repository.exists_by_email(normal_user.email)


@pytest.mark.asyncio
async def test_if_email_is_sent_with_token(
    use_case: RegisterUserUseCase,
    normal_user: User,
    default_plan: Plan,
    plain_password: PlainPassword,
    mock_email_template: EmailTemplate
):
    example_lang = Language.PT_BR
    plan = await use_case.plan_repository.add(default_plan)
    
    await use_case.execute(
        email=normal_user.email, 
        name=normal_user.name, 
        plan_pk=plan.pk,
        password=plain_password,
        lang=example_lang
    )

    expected_context = {
        "user_name": normal_user.name,
        "token": MockTokenService().mock_data["generated_tokens"][0],
        "expires_minutes": EMAIL_VERIFICATION_EXPIRES_IN.seconds * 60
    }

    template_result = mock_email_template.render(example_lang, expected_context)
    expected_email_log = {
        "to": normal_user.email,
        "subject": template_result["subject"],
        "plain_body": template_result["plain_body"],
        "html_body": template_result["html_body"]
    }

    email_log = MockSendEmailService().mock_logs[0]
    assert email_log == expected_email_log
