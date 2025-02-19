from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from .base import Base


class ShortURLModel(Base):
    __tablename__ = "shorturls"

    id = Column(Integer, primary_key=True)

    slug = Column(String, unique=True)
    original_url = Column(String, nullable=False)

    is_active = Column(Boolean, default=True, nullable=False)
    visit_count = Column(Integer, default=0, nullable=False)

    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    expires_at = Column(DateTime, nullable=True)
    last_accessed_at = Column(DateTime, nullable=True)


    def __repr__(self):
        return (
            f"<ShortURL(id={self.id}, slug='{self.slug}', "
            f"original_url='{self.original_url}', is_active={self.is_active})>"
        )
