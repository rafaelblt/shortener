from pydantic import BaseModel
from datetime import datetime

from shortener.domain.user import User


class PublicUserSchema(BaseModel):
    id: int
    name: str
    email: str
    plan_id: int
    created_at: datetime

    @staticmethod
    def from_domain(user: User):
        return PublicUserSchema(
            id=user.pk.get_id(),
            name=user.name,
            email=user.email,
            plan_id=user.plan.pk.get_id(),
            created_at=user.created_at
        )
