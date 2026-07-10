"""Business logic orchestration for cart price calculation.

This service is intentionally thin: the heavy lifting is delegated to
``PricingEngine``. Keeping a service wrapper (rather than having the
API router call ``PricingEngine`` directly) preserves the layering
convention used across the rest of the app -- routers only ever talk
to ``services``, never to ``engine`` or ``repositories`` directly.
"""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.engine.pricing_engine import PricingEngine
from app.schemas.bill import BillResponse
from app.schemas.cart import CartCalculateRequest
from app.validators.cart_validator import CartValidator


class CartService:
    """Coordinates cart price calculation via the ``PricingEngine``."""

    def __init__(self, db: Session) -> None:
        self.pricing_engine = PricingEngine(db)

    def calculate(self, request: CartCalculateRequest) -> BillResponse:
        """Price a cart, applying every eligible discount.

        Args:
            request: The customer, product lines, and optional coupon
                code to price.

        Returns:
            BillResponse: subtotal, applied discounts, total discount,
            and final payable amount.

        Raises:
            BadRequestException: If the cart contains duplicate
                product lines or non-positive quantities.
        """

        CartValidator.validate_no_duplicate_products(request.items)
        CartValidator.validate_positive_quantities(request.items)
        return self.pricing_engine.calculate(request)
