"""SQLAlchemy model for a Customer."""

from __future__ import annotations

from sqlalchemy import Enum as SAEnum
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constants import CustomerTier
from app.core.database import Base


class Customer(Base):
    """Represents a registered customer / shopper.

    Attributes:
        id: Primary key.
        name: Full name of the customer.
        email: Unique email address, used as a business key.
        tier: Loyalty tier (Silver, Gold, Platinum) used by
            ``CustomerTierDiscountStrategy`` to determine eligibility.
        carts: Carts belonging to this customer.
    """

    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    tier: Mapped[CustomerTier] = mapped_column(
        SAEnum(CustomerTier, native_enum=False),
        nullable=False,
        default=CustomerTier.SILVER,
    )

    carts: Mapped[list["Cart"]] = relationship(
        "Cart", back_populates="customer", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return f"<Customer id={self.id} email={self.email!r} tier={self.tier}>"
