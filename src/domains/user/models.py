from typing import Dict, Any
from decimal import Decimal
from datetime import datetime
from sqlalchemy import ForeignKey

from sqlalchemy.orm import Mapped, mapped_column, relationship
from lib.base_model import Base

class User(Base):
    __tablename__ = "user"

    name: Mapped[str] = mapped_column(index=True)
    username: Mapped[str] = mapped_column(unique=True, index=True)
    password: Mapped[str] = mapped_column()

    organisation_id: Mapped[str] = mapped_column(ForeignKey("organisation.id"), nullable=True)
    