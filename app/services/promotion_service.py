"""Business logic orchestration for the ``Promotion`` resource."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.exceptions.custom_exception import NotFoundException
from app.models.promotion import Promotion
from app.repositories.discount_repository import DiscountRepository
from app.repositories.promotion_repository import PromotionRepository
from app.schemas.promotion import PromotionCreate


class PromotionService:
    """Encapsulates business rules for creating and listing promotions."""

    def __init__(self, db: Session) -> None:
        self.repository = PromotionRepository(db)
        self.discount_repository = DiscountRepository(db)

    def create_promotion(self, payload: PromotionCreate) -> Promotion:
        """Schedule a new promotional window for a discount.

        Args:
            payload: Validated promotion creation data. The chronology
                of ``start_date``/``end_date`` is already enforced by
                ``PromotionBase``'s model validator.

        Returns:
            Promotion: The newly persisted promotion.

        Raises:
            NotFoundException: If ``payload.discount_id`` does not
                reference an existing discount.
        """

        discount = self.discount_repository.get_by_id(payload.discount_id)
        if discount is None:
            raise NotFoundException(f"Discount with id {payload.discount_id} not found.")

        promotion = Promotion(
            discount_id=payload.discount_id,
            start_date=payload.start_date,
            end_date=payload.end_date,
            active=payload.active,
        )
        return self.repository.create(promotion)

    def list_promotions(self, skip: int = 0, limit: int = 100) -> list[Promotion]:
        """Return a paginated list of all promotions."""

        return self.repository.list_all(skip=skip, limit=limit)
