from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship, attributes

from shortener.domain.shared.datetime_utils import utc_now

from shortener.domain.shorturl.fields import ShortURLStatus as Status
from shortener.domain.shorturl.fields.slug import SLUG_MAX_LENGTH

from shortener.infra.db.models.user import UserModel
from shortener.infra.db.exceptions import ModelRelationshipNotLoadedError

from .base import Base


class ShortURLModel(Base):
    __tablename__ = "shorturls"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String(SLUG_MAX_LENGTH), unique=True, nullable=False, index=True)
    original_url = Column(String, nullable=False)
    status = Column(Enum(Status), default=Status.ACTIVE, nullable=False)
    visit_count = Column(Integer(), default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: utc_now(), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    last_accessed_at = Column(DateTime(timezone=True), nullable=True)
    
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    owner = relationship("UserModel", back_populates="shorturls", lazy="selectin")


    def get_owner(self) -> UserModel:
        try:
            return self.owner
        except:
            raise ModelRelationshipNotLoadedError(instance=self, attr="owner")
    

    def __repr__(self):
        return (
            f"<ShortURLModel(id={self.id}, slug='{self.slug}', "
            f"original_url='{self.original_url}', owner_id={self.owner_id})>"
        )
