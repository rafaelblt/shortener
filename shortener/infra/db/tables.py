from typing import Final

from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
    Index,
    MetaData,
    Table,
    Text,
    UniqueConstraint,
    Uuid,
)


SLUG_UNIQUE_CONSTRAINT: Final = "uq_shorturls_slug"

metadata = MetaData()

shorturls = Table(
    "shorturls",
    metadata,
    Column("id", Uuid, primary_key=True),
    # The lengths of a slug and of a target URL are rules of create(), which
    # can change, so the columns don't limit them.
    # See docs/architecture/domain.md#value-objects
    Column("slug", Text, nullable=False),
    Column("target_url", Text, nullable=False),
    Column("owner_id", Uuid, nullable=False),
    Column("status", Text, nullable=False),
    Column("resolution_count", BigInteger, nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("last_resolved_at", DateTime(timezone=True), nullable=True),
    UniqueConstraint("slug", name=SLUG_UNIQUE_CONSTRAINT),
    # The listing reads the short URLs of an owner in this order.
    Index("ix_shorturls_owner_id_created_at_id", "owner_id", "created_at", "id"),
)
