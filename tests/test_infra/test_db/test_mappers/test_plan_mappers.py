from shortener.domain.plan import Plan

from shortener.domain.shared.primarykey import PrimaryKey

from shortener.infra.db.models import PlanModel
from shortener.infra.db.mappers import (
    map_plan_model_to_domain, map_plan_domain_to_model,
)

from tests.utils.entity_helpers import assert_plan_fields


def test_map_plan_domain_to_model(default_plan: Plan):
    retrieved = map_plan_domain_to_model(default_plan)

    assert isinstance(retrieved, PlanModel)
    assert_plan_fields(retrieved, default_plan)


def test_map_plan_model_to_domain(default_plan: Plan):
    default_plan._pk = PrimaryKey.create_pk_id(1)
    model = map_plan_domain_to_model(default_plan)

    retrieved = map_plan_model_to_domain(model)

    assert isinstance(retrieved, Plan)
    assert_plan_fields(retrieved, default_plan)
