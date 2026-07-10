"""Repository for ``Discount`` persistence operations."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.discount import Discount


class DiscountRepository:
    """Data-access layer for the ``Discount`` entity."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, discount: Discount) -> Discount:
        """Persist a new discount."""

        self.db.add(discount)
        self.db.commit()
        self.db.refresh(discount)
        return discount

    def get_by_id(self, discount_id: int) -> Discount | None:
        """Fetch a discount by primary key, or ``None`` if not found."""

        return self.db.get(Discount, discount_id)

    def get_by_coupon_code(self, coupon_code: str) -> Discount | None:
        """Fetch an active COUPON-type discount by its redemption code."""

        stmt = select(Discount).where(Discount.coupon_code == coupon_code)
        return self.db.scalars(stmt).first()

    def list_all(self, skip: int = 0, limit: int = 100) -> list[Discount]:
        """Return a paginated list of all discounts."""

        stmt = select(Discount).offset(skip).limit(limit)
        return list(self.db.scalars(stmt).all())

    def list_active(self) -> list[Discount]:
        """Return all discounts flagged as ``active``."""

        stmt = select(Discount).where(Discount.active.is_(True))
        return list(self.db.scalars(stmt).all())

    def update(self, discount: Discount) -> Discount:
        """Persist changes made to an already-tracked ``Discount``."""

        self.db.commit()
        self.db.refresh(discount)
        return discount

    def delete(self, discount: Discount) -> None:
        """Delete a discount and cascade-delete its promotions."""

        self.db.delete(discount)
        self.db.commit()
