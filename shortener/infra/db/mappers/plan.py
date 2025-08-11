from shortener.domain.shared.primarykey import PrimaryKey
from shortener.domain.plan import Plan

from shortener.infra.db.models.plan import PlanModel


def map_plan_domain_to_model(domain: Plan) -> PlanModel:
    return PlanModel(
        id=domain.pk.get_id() if domain.pk.is_id() else None,
        name=domain.name,
        max_shorturls=domain.max_shorturls
    )


def map_plan_model_to_domain(model: PlanModel) -> Plan:
    return Plan(
        pk=PrimaryKey.create_pk_id(model.id),
        name=model.name,
        max_shorturls=model.max_shorturls
    )
