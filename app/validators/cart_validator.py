"""Domain validation for cart-calculation requests.

These checks are business rules that go beyond what Pydantic's
stateless schema validation can express (``app.schemas.cart``), so
they live here and are invoked explicitly by the service layer.
"""

from __future__ import annotations

from app.exceptions.custom_exception import BadRequestException
from app.schemas.cart import CartItemInput


class CartValidator:
    """Validates business rules for a cart-calculation request."""

    @staticmethod
    def validate_no_duplicate_products(items: list[CartItemInput]) -> None:
        """Ensure no product appears more than once as a separate line.

        Duplicate lines for the same product are ambiguous for the
        Pricing Engine (which line's quantity should count towards a
        "Buy X Get Y" threshold?), so we require callers to consolidate
        quantities for the same product into a single line.

        Args:
            items: The cart lines supplied in the request.

        Raises:
            BadRequestException: If the same ``product_id`` appears in
                more than one line.
        """

        seen: set[int] = set()
        for item in items:
            if item.product_id in seen:
                raise BadRequestException(
                    f"Product id {item.product_id} appears more than once in the cart. "
                    "Consolidate duplicate product lines into a single quantity."
                )
            seen.add(item.product_id)

    @staticmethod
    def validate_positive_quantities(items: list[CartItemInput]) -> None:
        """Defensive re-check that every quantity is strictly positive.

        Pydantic's ``gt=0`` constraint on ``CartItemInput.quantity``
        already guarantees this at the schema boundary; this method
        exists so the same rule can be re-verified deeper in the call
        stack (e.g. if lines are constructed programmatically by
        internal code rather than via the HTTP layer).

        Raises:
            BadRequestException: If any quantity is not positive.
        """

        for item in items:
            if item.quantity <= 0:
                raise BadRequestException(
                    f"Quantity for product id {item.product_id} must be greater than zero."
                )
