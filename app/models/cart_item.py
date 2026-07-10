"""SQLAlchemy model for a CartItem (a product line within a Cart)."""

from __future__ import annotations

from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class CartItem(Base):
    """Represents a single product line within a shopping cart.

    Attributes:
        id: Primary key.
        cart_id: Foreign key to the owning ``Cart``.
        product_id: Foreign key to the referenced ``Product``.
        quantity: Number of units of the product in the cart. Must be > 0.
        cart: The related ``Cart`` row.
        product: The related ``Product`` row.
    """

    __tablename__ = "cart_items"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    cart_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("carts.id", ondelete="CASCADE"), nullable=False, index=True
    )
    product_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("products.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    cart: Mapped["Cart"] = relationship("Cart", back_populates="items")
    product: Mapped["Product"] = relationship("Product", back_populates="cart_items")

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return (
            f"<CartItem id={self.id} cart_id={self.cart_id} "
            f"product_id={self.product_id} quantity={self.quantity}>"
        )
