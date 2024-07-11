from typing import Dict, Any
from decimal import Decimal
from datetime import datetime
from sqlalchemy import ForeignKey

from sqlalchemy.orm import Mapped, mapped_column, relationship
from lib.base_model import Base

class Organisation(Base):
    __tablename__ = "organisation"

    name: Mapped[str] = mapped_column(index=True)
    description: Mapped[str] = mapped_column(unique=True, nullable=True)
    invite_code: Mapped[str] = mapped_column(unique=True, index=True)
    logo_url: Mapped[str] = mapped_column(nullable=True)
    