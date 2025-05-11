import pytest

from tests.utils.entity_helpers import (
    assert_plan_fields, assert_user_fields, assert_shorturl_fields
)

from shortener.domain.plan import Plan
from shortener.domain.user import User
from shortener.domain.shorturl import ShortURL

from shortener.infra.db.models import PlanModel, UserModel, ShortURLModel

from shortener.infra.db.mappers import (
    map_plan_model_to_domain, map_plan_domain_to_model,
    map_user_model_to_domain, map_user_domain_to_model,
    map_shorturl_model_to_domain, map_shorturl_domain_to_model
)


def test_map_plan_domain_to_model(default_plan: Plan):
    retrieved = map_plan_domain_to_model(default_plan)
    assert isinstance(retrieved, PlanModel)
    assert_plan_fields(retrieved, default_plan)


def test_map_plan_model_to_domain(default_plan: Plan):
    model = map_plan_domain_to_model(default_plan)
    retrieved = map_plan_model_to_domain(model)
    assert isinstance(retrieved, Plan)
    assert_plan_fields(retrieved, default_plan)


@pytest.mark.asyncio
async def test_map_user_domain_to_model(normal_user: User):
    normal_user.plan._id = 1
    retrieved = map_user_domain_to_model(normal_user)
    assert isinstance(retrieved, UserModel)
    retrieved.plan_id = normal_user.plan.id
    assert_user_fields(retrieved, normal_user)


def test_map_user_model_to_domain(normal_user: User, default_plan: Plan):
    normal_user.plan._id = 1
    user_model = map_user_domain_to_model(normal_user)

    plan_model = map_plan_domain_to_model(default_plan)
    user_model.plan = plan_model

    retrieved = map_user_model_to_domain(user_model)

    assert isinstance(retrieved, User)
    assert_user_fields(retrieved, normal_user)


@pytest.mark.asyncio
async def test_map_shorturl_domain_to_model(normal_shorturl: ShortURL):
    normal_shorturl.owner._id = 1
    retrieved = map_shorturl_domain_to_model(normal_shorturl)
    assert isinstance(retrieved, ShortURLModel)
    retrieved.owner_id = normal_shorturl.owner.id
    assert_shorturl_fields(retrieved, normal_shorturl)


def test_map_shorturl_model_to_domain(
    normal_shorturl: ShortURL,
    normal_user: User,
    default_plan: Plan
):
    plan_model = map_plan_domain_to_model(default_plan)

    normal_user.plan._id = 1
    user_model = map_user_domain_to_model(normal_user)
    user_model.plan = plan_model
    
    normal_shorturl.owner._id = 1
    shorturl_model = map_shorturl_domain_to_model(normal_shorturl)
    shorturl_model.owner = user_model

    retrieved = map_shorturl_model_to_domain(shorturl_model)

    assert isinstance(retrieved, ShortURL)
    assert_shorturl_fields(retrieved, normal_shorturl)
