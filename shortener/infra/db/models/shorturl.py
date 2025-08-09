from datetime import datetime

from sqlalchemy import Integer, String, DateTime, Enum, ForeignKey
from sqlalchemy.exc import MissingGreenlet
from sqlalchemy.orm import Mapped, mapped_column, relationship

from shortener.domain.shared.datetime_utils import utc_now

from shortener.domain.shorturl.fields import ShortURLStatus as Status
from shortener.domain.shorturl.fields.slug import SLUG_MAX_LENGTH

from shortener.infra.db.models.user import UserModel
from shortener.infra.db.exceptions import ModelRelationshipNotLoadedError

from .base import Base


class ShortURLModel(Base):
    __tablename__ = "shorturls"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True
    )
    slug: Mapped[str] = mapped_column(
        String(SLUG_MAX_LENGTH), unique=True, nullable=False, index=True
    )
    original_url: Mapped[str] = mapped_column(
        String, nullable=False
    )
    status: Mapped[Status] = mapped_column(
        Enum(Status), default=Status.ACTIVE, nullable=False
    )
    visit_count: Mapped[int] = mapped_column(
        Integer(), default=0, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: utc_now(), nullable=False
    )
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    last_accessed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    owner_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    owner = relationship(
        "UserModel", back_populates="shorturls", lazy="selectin"
    )


    def get_owner(self) -> UserModel:
        try:
            return self.owner
        except MissingGreenlet:
            raise ModelRelationshipNotLoadedError(instance=self, attr="owner")
    

    def __repr__(self):
        return (
            f"<ShortURLModel(id={self.id}, slug='{self.slug}', "
            f"original_url='{self.original_url}')>"
        )
