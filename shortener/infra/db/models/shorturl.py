from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship

from shortener.domain.shorturl.fields import ShortURLStatus
from shortener.domain.shorturl.fields.slug import SLUG_MAX_LENGTH


from .base import Base


class ShortURLModel(Base):
    __tablename__ = "shorturls"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String(SLUG_MAX_LENGTH), unique=True, nullable=False, index=True)
    original_url = Column(String, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    status = Column(
        Enum(ShortURLStatus), default=ShortURLStatus.ACTIVE, nullable=False
    )
    visit_count = Column(Integer, default=0, nullable=False)
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    expires_at = Column(DateTime, nullable=True)
    last_accessed_at = Column(DateTime, nullable=True)

    owner = relationship("UserModel", back_populates="shorturls")

    def __repr__(self):
        return (
            f"<ShortURLModel(id={self.id}, slug='{self.slug}', "
            f"original_url='{self.original_url}', status={self.status})>"
        )
