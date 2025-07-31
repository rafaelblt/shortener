from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, relationship, mapped_column

from .base import Base


class PlanModel(Base):
    __tablename__ = "plans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    max_shorturls: Mapped[int] = mapped_column(Integer, nullable=False)

    users = relationship("UserModel", back_populates="plan")
