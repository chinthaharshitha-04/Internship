"""SQLAlchemy model for a shopping Cart."""

from __future__ import annotations

from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Cart(Base):
    """Represents a shopping cart owned by a customer.

    Attributes:
        id: Primary key.
        customer_id: Foreign key to the owning ``Customer``.
        customer: The related ``Customer`` row.
        items: Line items contained in this cart.
    """

    __tablename__ = "carts"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    customer_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, index=True
    )

    customer: Mapped["Customer"] = relationship("Customer", back_populates="carts")
    items: Mapped[list["CartItem"]] = relationship(
        "CartItem", back_populates="cart", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return f"<Cart id={self.id} customer_id={self.customer_id}>"
