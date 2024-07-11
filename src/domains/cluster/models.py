from typing import Dict, Any
from decimal import Decimal
from datetime import datetime
from sqlalchemy import ForeignKey

from sqlalchemy.orm import Mapped, mapped_column, relationship
from lib.base_model import Base

class Cluster(Base):
    __tablename__ = "cluster"

    name: Mapped[str] = mapped_column(index=True)
    description: Mapped[str] = mapped_column(nullable=True)

    cpu_allocated: Mapped[Decimal] = mapped_column()
    memory_allocated: Mapped[Decimal] = mapped_column()

    organisation_id: Mapped[str] = mapped_column(ForeignKey("organisation.id"))
    created_by: Mapped[str] = mapped_column(ForeignKey("user.id"))    

    notes: Mapped[str] = mapped_column(nullable=True)