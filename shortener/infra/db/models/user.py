from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship

from shortener.domain.shared.datetime_utils import utc_now

from shortener.domain.user.fields import UserStatus
from shortener.domain.user.fields.name import NAME_MAX_LENGTH

from .base import Base


class UserModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    name = Column(String(NAME_MAX_LENGTH), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    status = Column(Enum(UserStatus), default=UserStatus.ACTIVE, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=lambda: utc_now(), nullable=False)
    last_login = Column(DateTime, nullable=True)

    plan_id = Column(Integer, ForeignKey("plans.id"), nullable=False)

    shorturls = relationship(
        "ShortURLModel", back_populates="owner", cascade="all, delete-orphan"
    )
    plan = relationship("PlanModel", back_populates="users")

    def __repr__(self):
        return (
            f"<UserModel(id={self.id}, email='{self.email}', "
            f"name='{self.name}', status={self.status})>"
        )
