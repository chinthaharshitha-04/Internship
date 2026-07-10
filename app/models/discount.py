"""SQLAlchemy model for a Discount rule."""

from __future__ import annotations

from sqlalchemy import Boolean, Enum as SAEnum, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constants import CustomerTier, DiscountType
from app.core.database import Base


class Discount(Base):
    """Represents a configurable discount rule.

    A single table is used to back every ``DiscountStrategy``
    implementation (the classic "single table inheritance via
    discriminator" approach). Only the columns relevant to ``type``
    are expected to be populated for a given row; the rest remain
    ``None``. This keeps persistence simple while the Strategy pattern
    keeps the *behavior* for each type cleanly separated in the
    ``app.strategies`` package.

    Attributes:
        id: Primary key.
        name: Human-readable discount name (e.g. "Summer Sale 20%").
        type: Discriminator selecting which ``DiscountStrategy`` applies.
        value: Generic numeric value -- percentage for PERCENTAGE,
            flat amount for FLAT, percentage for COUPON, etc.
        minimum_purchase: Minimum cart subtotal required for eligibility.
        is_stackable: Whether this discount can combine with others.
        priority: Lower number = higher priority when selecting among
            non-stackable discounts.
        active: Soft-delete / enable-disable flag.
        buy_quantity: "Buy X" quantity, used by BUY_X_GET_Y.
        get_quantity: "Get Y free" quantity, used by BUY_X_GET_Y.
        applicable_category: Category name, used by CATEGORY.
        required_tier: Minimum customer tier, used by CUSTOMER_TIER.
        coupon_code: Redemption code, used by COUPON.
    """

    __tablename__ = "discounts"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    type: Mapped[DiscountType] = mapped_column(
        SAEnum(DiscountType, native_enum=False), nullable=False, index=True
    )
    value: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    minimum_purchase: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    is_stackable: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=100)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # Strategy-specific optional configuration.
    buy_quantity: Mapped[int | None] = mapped_column(Integer, nullable=True)
    get_quantity: Mapped[int | None] = mapped_column(Integer, nullable=True)
    applicable_category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    required_tier: Mapped[CustomerTier | None] = mapped_column(
        SAEnum(CustomerTier, native_enum=False), nullable=True
    )
    coupon_code: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)

    promotions: Mapped[list["Promotion"]] = relationship(
        "Promotion", back_populates="discount", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return f"<Discount id={self.id} name={self.name!r} type={self.type}>"
