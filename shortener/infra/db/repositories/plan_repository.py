from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from shortener.domain.plan import Plan, PlanRepository
from shortener.domain.plan.exceptions import PlanNotFoundError

from shortener.infra.db.mappers import (
    map_plan_model_to_domain, map_plan_domain_to_model
)

from shortener.infra.db.models import PlanModel


class SQLAlchemyPlanRepository(PlanRepository):
    """SQLAlchemy implementation of PlanRepository."""

    def __init__(self, session: AsyncSession):
        """
        Args:
            session (Session): SQLAlchemy Async Session instance.
        """
        self.session = session

    async def add(self, plan: Plan) -> Plan:
        model = self._to_model(plan)
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return self._to_domain(model)

    async def update(self, plan: Plan) -> Plan:
        plan_id = plan.get_int_id()
        
        existing_model = await self._get_model_by_id(plan_id)
        if existing_model is None:
            raise PlanNotFoundError(plan_id=plan_id)

        existing_model.name = plan.name
        existing_model.max_shorturls = plan.max_shorturls

        await self.session.commit()
        await self.session.refresh(existing_model)

        return self._to_domain(existing_model)

    async def get_all(self) -> list[Plan]:
        models = await self._get_all_models()
        return [self._to_domain(model) for model in models]

    async def get_by_id(self, id: int) -> Plan | None:
        model = await self._get_model_by_id(id)
        return self._to_domain(model) if model else None

    async def delete_by_id(self, id: int) -> Plan:
        model = await self._get_model_by_id(id)
        if model is None:
            raise PlanNotFoundError(plan_id=id)

        await self.session.delete(model)
        await self.session.commit()
        return self._to_domain(model)

    async def _get_all_models(self) -> Sequence[PlanModel]:
        result = await self.session.scalars(select(PlanModel))
        return result.all()

    async def _get_model_by_id(self, id: int) -> PlanModel | None:
        """
        Retrieves a PlanModel by its id.

        Args:
            id (int): The PlanModel id.

        Returns:
            Optional[PlanModel]: The model object or None if not found.
        """
        model = await self.session.get(PlanModel, id)
        return model

    def _to_domain(self, model: PlanModel) -> Plan:
        """Converts a SQLAlchemy model instance to a domain entity."""
        return map_plan_model_to_domain(model)

    def _to_model(self, entity: Plan) -> PlanModel:
        """Converts a domain entity to a SQLAlchemy model instance."""
        return map_plan_domain_to_model(entity)