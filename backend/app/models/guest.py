"""
Guest model — anonymous shopping sessions identified by UUID.
"""
from sqlalchemy import String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from app.database import Base


class Guest(Base):
    __tablename__ = "guests"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    guest_id: Mapped[str] = mapped_column(String(36), unique=True, nullable=False, index=True)  # UUID
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    cart_items: Mapped[list["Cart"]] = relationship("Cart", back_populates="guest")
