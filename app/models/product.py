"""SQLAlchemy model for a Product."""

from __future__ import annotations

from sqlalchemy import Float, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Product(Base):
    """Represents a sellable product in the catalogue.

    Attributes:
        id: Primary key.
        name: Display name of the product.
        category: Category used by ``CategoryDiscountStrategy`` (e.g.
            "Apparel", "Electronics").
        price: Unit price. Must be strictly positive.
        cart_items: Cart line items referencing this product.
    """

    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    price: Mapped[float] = mapped_column(Float, nullable=False)

    cart_items: Mapped[list["CartItem"]] = relationship(
        "CartItem", back_populates="product"
    )

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return f"<Product id={self.id} name={self.name!r} price={self.price}>"
