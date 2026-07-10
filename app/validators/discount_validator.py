"""Domain validation for discount rules.

These checks require querying the database (e.g. "is this coupon
code already used?"), which is precisely the kind of stateful
validation Pydantic's schema layer cannot perform -- hence a
dedicated validator invoked from the service layer.
"""

from __future__ import annotations

from app.exceptions.custom_exception import DuplicateResourceException
from app.repositories.discount_repository import DiscountRepository


class DiscountValidator:
    """Validates business rules for discount creation/updates."""

    def __init__(self, repository: DiscountRepository) -> None:
        self.repository = repository

    def validate_unique_coupon_code(
        self, coupon_code: str | None, exclude_discount_id: int | None = None
    ) -> None:
        """Ensure a coupon code is not already registered on another discount.

        Args:
            coupon_code: The coupon code to check, or ``None`` for
                discount types that don't use one (in which case this
                is a no-op).
            exclude_discount_id: When updating an existing discount,
                its own id, so re-saving the same code on itself
                doesn't trigger a false positive.

        Raises:
            DuplicateResourceException: If another discount already
                uses ``coupon_code``.
        """

        if not coupon_code:
            return

        existing = self.repository.get_by_coupon_code(coupon_code)
        if existing is not None and existing.id != exclude_discount_id:
            raise DuplicateResourceException(
                f"Coupon code '{coupon_code}' is already in use by another discount."
            )
