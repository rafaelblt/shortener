import pytest

from shortener.domain.shared.primarykey import PrimaryKey

from shortener.domain.refresh_token import RefreshToken
from shortener.domain.user import User

from shortener.infra.db.models import RefreshTokenModel
from shortener.infra.db.mappers import (
    map_plan_domain_to_model,
    map_user_domain_to_model,
    map_refresh_token_model_to_domain, map_refresh_token_domain_to_model
)

from tests.utils.entity_helpers import assert_refresh_token_fields


def test_map_refresh_token_domain_to_model(active_refresh_token: RefreshToken):
    active_refresh_token.user._pk = PrimaryKey.create_pk_id(1)

    retrieved = map_refresh_token_domain_to_model(active_refresh_token)

    assert isinstance(retrieved, RefreshTokenModel)
    assert_refresh_token_fields(retrieved, active_refresh_token)


def test_map_refresh_token_model_to_domain(
    active_refresh_token: RefreshToken, normal_user: User
):
    active_refresh_token._pk = PrimaryKey.create_pk_id(1)
    active_refresh_token.user._pk = PrimaryKey.create_pk_id(1)
    normal_user.plan._pk = PrimaryKey.create_pk_id(1)

    user_model = map_user_domain_to_model(normal_user)
    plan_model = map_plan_domain_to_model(normal_user.plan)
    user_model.plan = plan_model
    token_model = map_refresh_token_domain_to_model(active_refresh_token)
    token_model.user = user_model

    retrieved = map_refresh_token_model_to_domain(token_model)

    assert isinstance(retrieved, RefreshToken)
    assert_refresh_token_fields(retrieved, active_refresh_token)
