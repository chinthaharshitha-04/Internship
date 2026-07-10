"""Repository for ``Promotion`` persistence operations."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.promotion import Promotion


class PromotionRepository:
    """Data-access layer for the ``Promotion`` entity."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, promotion: Promotion) -> Promotion:
        """Persist a new promotion."""

        self.db.add(promotion)
        self.db.commit()
        self.db.refresh(promotion)
        return promotion

    def get_by_id(self, promotion_id: int) -> Promotion | None:
        """Fetch a promotion by primary key, or ``None`` if not found."""

        return self.db.get(Promotion, promotion_id)

    def list_all(self, skip: int = 0, limit: int = 100) -> list[Promotion]:
        """Return a paginated list of all promotions."""

        stmt = select(Promotion).offset(skip).limit(limit)
        return list(self.db.scalars(stmt).all())

    def list_active_within_window(self, at: datetime | None = None) -> list[Promotion]:
        """Return promotions that are active and currently within their date window.

        Args:
            at: The reference timestamp to check against. Defaults to
                the current UTC time.

        Returns:
            list[Promotion]: Promotions eagerly loaded with their
            related ``Discount``, so the Pricing Engine can evaluate
            them without triggering additional queries per row (avoids
            the N+1 query problem).
        """

        reference_time = at or datetime.utcnow()
        stmt = (
            select(Promotion)
            .options(joinedload(Promotion.discount))
            .where(
                Promotion.active.is_(True),
                Promotion.start_date <= reference_time,
                Promotion.end_date >= reference_time,
            )
        )
        return list(self.db.scalars(stmt).unique().all())

    def delete(self, promotion: Promotion) -> None:
        """Delete a promotion."""

        self.db.delete(promotion)
        self.db.commit()
