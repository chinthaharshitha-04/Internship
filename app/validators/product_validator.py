"""Domain validation for product data."""

from __future__ import annotations

from app.core.constants import MIN_PRICE
from app.exceptions.custom_exception import BadRequestException


class ProductValidator:
    """Validates business rules for product creation/updates.

    Complements the structural checks already performed by
    ``app.schemas.product`` (e.g. ``price: float = Field(..., gt=0)``)
    with rules that are more naturally expressed as explicit,
    reusable, unit-testable functions.
    """

    @staticmethod
    def validate_price(price: float) -> None:
        """Ensure a price is strictly positive and at least the minimum unit.

        Args:
            price: The unit price to validate.

        Raises:
            BadRequestException: If ``price`` is not a valid positive
                amount.
        """

        if price is None or price < MIN_PRICE:
            raise BadRequestException(f"Product price must be at least {MIN_PRICE}.")

    @staticmethod
    def validate_category(category: str) -> None:
        """Ensure a category name is non-blank once whitespace is stripped.

        Args:
            category: The category name to validate.

        Raises:
            BadRequestException: If ``category`` is empty or whitespace-only.
        """

        if not category or not category.strip():
            raise BadRequestException("Product category must not be blank.")
