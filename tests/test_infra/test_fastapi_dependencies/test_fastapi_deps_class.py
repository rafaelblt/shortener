from shortener.infra.dependencies import fastapi_deps

from shortener.infra.dependencies.fastapi.db.repositories import (
    get_plan_repository, get_shorturl_repository, get_user_repository
)
from shortener.infra.dependencies.fastapi.services import (
    get_access_auth_token_service,
    get_verify_email_auth_token_service,
    get_password_hasher_service,
    get_refresh_auth_token_service,
    get_send_email_service
)
from shortener.infra.dependencies.fastapi.use_cases import (
    make_create_shorturl_for_user_use_case,
    make_create_shorturl_use_case,
    make_delete_shorturl_use_case,
    make_get_shorturl_use_case,
    make_list_shorturl_use_case,
    make_login_user_use_case,
    make_refresh_login_use_case,
    make_register_user_use_case,
    make_resolve_shorturl_use_case,
    make_update_shorturl_use_case,
    make_verify_email_use_case,
)


def test_fastapi_deps_attributes():
    assert fastapi_deps.plan_repository.dependency == get_plan_repository().dependency
    assert fastapi_deps.shorturl_repository.dependency == get_shorturl_repository().dependency
    assert fastapi_deps.user_repository.dependency == get_user_repository().dependency

    assert fastapi_deps.access_token_service.dependency == get_access_auth_token_service().dependency
    assert fastapi_deps.verify_email_token_service.dependency == get_verify_email_auth_token_service().dependency
    assert fastapi_deps.password_hasher_service.dependency == get_password_hasher_service().dependency
    assert fastapi_deps.refresh_token_service.dependency == get_refresh_auth_token_service().dependency
    assert fastapi_deps.send_email_service.dependency == get_send_email_service().dependency

    assert fastapi_deps.register_user_use_case.dependency == make_register_user_use_case
    assert fastapi_deps.login_user_use_case.dependency == make_login_user_use_case
    assert fastapi_deps.verify_email_use_case.dependency == make_verify_email_use_case
    assert fastapi_deps.refresh_login_use_case.dependency == make_refresh_login_use_case
    assert fastapi_deps.create_shorturl_use_case.dependency == make_create_shorturl_use_case
    assert fastapi_deps.create_shorturl_for_user_use_case.dependency == make_create_shorturl_for_user_use_case
    assert fastapi_deps.delete_shorturl_use_case.dependency == make_delete_shorturl_use_case
    assert fastapi_deps.get_shorturl_use_case.dependency == make_get_shorturl_use_case
    assert fastapi_deps.list_shorturl_use_case.dependency == make_list_shorturl_use_case
    assert fastapi_deps.resolve_shorturl_use_case.dependency == make_resolve_shorturl_use_case
    assert fastapi_deps.update_shorturl_use_case.dependency == make_update_shorturl_use_case
