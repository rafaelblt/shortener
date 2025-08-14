from shortener.domain.shared.primarykey import PrimaryKey

from shortener.domain.user import User

from shortener.infra.db.models import  UserModel
from shortener.infra.db.mappers import (
    map_user_model_to_domain, map_user_domain_to_model,
    map_plan_domain_to_model
)

from tests.utils.entity_helpers import assert_user_fields


def test_map_user_domain_to_model(normal_user: User):
    normal_user.plan._pk = PrimaryKey.create_pk_id(1)

    retrieved = map_user_domain_to_model(normal_user)
    
    assert isinstance(retrieved, UserModel)
    assert_user_fields(retrieved, normal_user)


def test_map_user_model_to_domain(normal_user: User):
    normal_user._pk = PrimaryKey.create_pk_id(1)
    normal_user.plan._pk = PrimaryKey.create_pk_id(1)

    user_model = map_user_domain_to_model(normal_user)
    plan_model = map_plan_domain_to_model(normal_user.plan)
    user_model.plan = plan_model

    retrieved = map_user_model_to_domain(user_model)

    assert isinstance(retrieved, User)
    assert_user_fields(retrieved, normal_user)
