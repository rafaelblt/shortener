from datetime import datetime
from typing import List

from sqlalchemy import Integer, String, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import Mapped, relationship, mapped_column

from shortener.domain.shared.datetime_utils import utc_now

from shortener.domain.user.fields import UserStatus
from shortener.domain.user.fields.name import NAME_MAX_LENGTH

from shortener.infra.db.models.plan import PlanModel
from shortener.infra.db.exceptions import ModelRelationshipNotLoadedError

from .base import Base


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True
    )
    email: Mapped[str] = mapped_column(
        String, unique=True, index=True, nullable=False
    )
    name: Mapped[str] = mapped_column(
        String(NAME_MAX_LENGTH), nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(
        String(255), nullable=False
    )
    status: Mapped[UserStatus] = mapped_column(
        Enum(UserStatus), default=UserStatus.ACTIVE, nullable=False
    )
    is_superuser: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: utc_now(), nullable=False
    )
    last_login: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    plan_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("plans.id", ondelete="SET NULL"), nullable=True
    )
    shorturls = relationship(
        "ShortURLModel", back_populates="owner", cascade="all, delete-orphan"
    )
    plan = relationship(
        "PlanModel", back_populates="users", lazy="selectin"
    )


    def get_plan(self) -> PlanModel:
        try:
            return self.plan
        except:
            raise ModelRelationshipNotLoadedError(instance=self, attr="plan")
        
    def get_shorturls(self) -> List["ShortURLModel"]:
        try:
            return self.shorturls
        except:
            raise ModelRelationshipNotLoadedError(instance=self, attr="shorturls")


    def __repr__(self):
        return (
            f"<UserModel(id={self.id}, email='{self.email}', "
            f"name='{self.name}', status={self.status})>"
        )


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from shortener.infra.db.models.shorturl import ShortURLModel
