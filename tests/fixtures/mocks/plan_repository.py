from shortener.domain.shared.pagination import PaginatedResult

from shortener.domain.plan import Plan, PlanRepository
from shortener.domain.plan.exceptions import PlanNotFoundInDatabaseError

from .database import MockDatabase, IdManager


class MockPlanRepository(PlanRepository):
    def __init__(self):
        self.database = MockDatabase(index_manager=IdManager())

    async def add(self, plan: Plan) -> Plan:
        plan_dict = self._to_dict(plan)
        plan_dict = self.database.add(entity=plan_dict)
        return self._to_domain(plan_dict)
    
    async def update(self, plan: Plan) -> Plan:
        if not self.database.exists_by_index(plan.id):
            raise PlanNotFoundInDatabaseError(
                f"Plan with id={plan.id} not found in MockPlanRepository."
            )

        plan_dict = self.database.get_by_index(plan.id)
        plan_dict["name"] = plan.name
        plan_dict["max_shorturls"] = plan.max_shorturls
    
        return self._to_domain(plan_dict)
    
    async def get_all(self) -> list[Plan]:
        return [self._to_domain(entity) for entity in self.database.get_all()]

    async def get_by_id(self, id: int) -> Plan | None:
        plan_dict = self.database.get_by_index(id)
        if plan_dict:
            return self._to_domain(plan_dict)
        return None

    async def delete_by_id(self, id: int) -> Plan:
        plan_dict = self.database.delete_by_index(id)
        if plan_dict:
            return self._to_domain(plan_dict)
        raise PlanNotFoundInDatabaseError(
            f"Plan with id={id} not found in MockPlanRepository."
        )
            
    def _to_dict(self, plan: Plan) -> dict:
        return {
            "pk": plan.id,
            "name": plan.name,
            "max_shorturls": plan.max_shorturls
        }
    
    def _to_domain(self, plan_dict: dict) -> Plan:
        return Plan(
            id=plan_dict["pk"],
            name=plan_dict["name"],
            max_shorturls=plan_dict["max_shorturls"]
        ) 
