from fastapi.params import Depends

from shortener.infra.dependencies.fastapi.db.repositories import (
    get_user_repository,
    get_plan_repository,
)
from shortener.infra.dependencies.fastapi.services import (
    get_password_hasher_service,
    get_verify_email_auth_token_service,
    get_send_email_service
)
from shortener.infra.dependencies.fastapi.use_cases import make_register_user_use_case

from shortener.infra.templates.jinja.auth import VerificationEmailTemplate
from shortener.infra.templates.jinja.environment import JinjaEnvironment

from shortener.use_cases import RegisterUserUseCase


def test_dependency_factory():
    retrieved = make_register_user_use_case()

    assert isinstance(retrieved, RegisterUserUseCase)

    assert isinstance(retrieved.user_repository, Depends)
    assert retrieved.user_repository.dependency == get_user_repository().dependency

    assert isinstance(retrieved.plan_repository, Depends)
    assert retrieved.plan_repository.dependency == get_plan_repository().dependency

    assert isinstance(retrieved.send_email_service, Depends)
    assert retrieved.send_email_service.dependency == get_send_email_service().dependency

    assert isinstance(retrieved.password_hasher, Depends)
    assert retrieved.password_hasher.dependency == get_password_hasher_service().dependency

    assert isinstance(retrieved.email_template, VerificationEmailTemplate)
    assert isinstance(retrieved.email_template._jinja_env, JinjaEnvironment)

    assert isinstance(retrieved.token_service, Depends)
    assert retrieved.token_service.dependency == get_verify_email_auth_token_service().dependency
