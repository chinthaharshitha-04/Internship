"""SQLAlchemy model for a Promotion (time-boxed activation of a Discount)."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Promotion(Base):
    """Represents a scheduled promotional window for a ``Discount``.

    Separating ``Promotion`` from ``Discount`` allows the same
    discount rule to be scheduled for multiple, non-overlapping
    campaigns without duplicating its configuration.

    Attributes:
        id: Primary key.
        discount_id: Foreign key to the associated ``Discount``.
        start_date: Timestamp from which the promotion is valid.
        end_date: Timestamp after which the promotion expires.
        active: Manual on/off switch, independent of the date window.
        discount: The related ``Discount`` row.
    """

    __tablename__ = "promotions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    discount_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("discounts.id", ondelete="CASCADE"), nullable=False, index=True
    )
    start_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    discount: Mapped["Discount"] = relationship("Discount", back_populates="promotions")

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return (
            f"<Promotion id={self.id} discount_id={self.discount_id} "
            f"start={self.start_date} end={self.end_date}>"
        )
