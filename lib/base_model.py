from datetime import datetime
from sqlalchemy.types import TIMESTAMP
from sqlalchemy import func, String

# from sqlalchemy.orm import declared_attr
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


# https://docs.sqlalchemy.org/en/20/orm/declarative_mixins.html#augmenting-the-base
class Base(DeclarativeBase):
    """define a series of common elements that may be applied to mapped classes
    using this class as a base class."""

    id: Mapped[str] = mapped_column(String(19), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), default=func.now(), nullable=True, index=True) # timezone aware datetime in utc
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), default=func.now(), onupdate=func.now(), nullable=True, index=True) # timezone aware datetime in utc
