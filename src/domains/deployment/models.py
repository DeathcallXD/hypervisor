from typing import Dict, Any
from decimal import Decimal
from datetime import datetime
from sqlalchemy import ForeignKey

from sqlalchemy.orm import Mapped, mapped_column, relationship
from lib.base_model import Base

class Deployment(Base):
    __tablename__ = "deployment"

    name: Mapped[str] = mapped_column(index=True)
    description: Mapped[str] = mapped_column(nullable=True)

    priority: Mapped[int] = mapped_column(index=True)
    cpu_allocated: Mapped[Decimal] = mapped_column()
    memory_allocated: Mapped[Decimal] = mapped_column()
    path_to_docker_image: Mapped[str] = mapped_column(index=True)

    status: Mapped[str] = mapped_column(index=True)

    organisation_id: Mapped[str] = mapped_column(ForeignKey("organisation.id"))
    cluster_id: Mapped[str] = mapped_column(ForeignKey("cluster.id"))
    created_by: Mapped[str] = mapped_column(ForeignKey("user.id"))    

    notes: Mapped[str] = mapped_column(nullable=True)