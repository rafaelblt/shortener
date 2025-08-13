from datetime import datetime

from sqlalchemy import Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.exc import MissingGreenlet
from sqlalchemy.orm import Mapped, relationship, mapped_column

from shortener.domain.shared.datetime_utils import utc_now

from shortener.infra.db.exceptions import ModelRelationshipNotLoadedError
from shortener.infra.db.models.user import UserModel

from .base import Base


class RefreshTokenModel(Base):
    __tablename__ = "refresh_tokens"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True
    )
    token: Mapped[str] = mapped_column(
        String, unique=True, index=True
    )
    revoked: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: utc_now(), nullable=False
    )
    user_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True
    )
    user = relationship(
        "UserModel", back_populates="refresh_tokens", lazy="selectin"
    )


    def get_user(self) -> UserModel:
        try:
            return self.user
        except MissingGreenlet as e:
            raise ModelRelationshipNotLoadedError(instance=self, attr="user")


    def __repr__(self):
        return (f"<RefreshTokenModel(id={self.id})>")
