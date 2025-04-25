from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from .base import Base


class PlanModel(Base):
    __tablename__ = "plans"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    max_shorturls = Column(Integer, nullable=False)

    users = relationship("UserModel", back_populates="plan")
