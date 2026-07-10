"""Business logic orchestration for the ``Discount`` resource."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.exceptions.custom_exception import NotFoundException
from app.models.discount import Discount
from app.repositories.discount_repository import DiscountRepository
from app.schemas.discount import DiscountCreate, DiscountUpdate
from app.validators.discount_validator import DiscountValidator


class DiscountService:
    """Encapsulates business rules for creating and managing discounts."""

    def __init__(self, db: Session) -> None:
        self.repository = DiscountRepository(db)
        self.validator = DiscountValidator(self.repository)

    def create_discount(self, payload: DiscountCreate) -> Discount:
        """Create a new discount rule.

        Type-specific field validation (e.g. requiring
        ``applicable_category`` for CATEGORY discounts) is already
        enforced by ``DiscountCreate``'s Pydantic model validator, so
        by the time we reach this service the payload is guaranteed
        internally consistent. ``DiscountValidator`` additionally
        guards against coupon-code collisions across discounts, which
        requires a database lookup Pydantic cannot perform.

        Args:
            payload: Validated discount creation data.

        Returns:
            Discount: The newly persisted discount.

        Raises:
            DuplicateResourceException: If ``payload.coupon_code`` is
                already used by another discount.
        """

        self.validator.validate_unique_coupon_code(payload.coupon_code)

        discount = Discount(**payload.model_dump())
        return self.repository.create(discount)

    def get_discount(self, discount_id: int) -> Discount:
        """Fetch a discount by id.

        Raises:
            NotFoundException: If no such discount exists.
        """

        discount = self.repository.get_by_id(discount_id)
        if discount is None:
            raise NotFoundException(f"Discount with id {discount_id} not found.")
        return discount

    def list_discounts(self, skip: int = 0, limit: int = 100) -> list[Discount]:
        """Return a paginated list of discounts."""

        return self.repository.list_all(skip=skip, limit=limit)

    def update_discount(self, discount_id: int, payload: DiscountUpdate) -> Discount:
        """Apply a partial update to an existing discount.

        Raises:
            NotFoundException: If no such discount exists.
        """

        discount = self.get_discount(discount_id)

        updates = payload.model_dump(exclude_unset=True)

        if "coupon_code" in updates:
            self.validator.validate_unique_coupon_code(
                updates["coupon_code"], exclude_discount_id=discount_id
            )

        for field, value in updates.items():
            setattr(discount, field, value)

        return self.repository.update(discount)

    def delete_discount(self, discount_id: int) -> None:
        """Delete a discount.

        Raises:
            NotFoundException: If no such discount exists.
        """

        discount = self.get_discount(discount_id)
        self.repository.delete(discount)
