"""Pricing Engine: orchestrates end-to-end cart price calculation.

Responsibilities (per the assignment spec):
    * Read all active promotions.
    * Check eligibility for each (delegated to the Strategy layer).
    * Ignore expired promotions (delegated to the repository's
      date-window filtering).
    * Apply priority and respect the stackable flag when selecting the
      final set of discounts (delegated to the ``RuleEngine``).
    * Return the subtotal, applied discount list, total discount, and
      final payable amount.
"""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.engine.rule_engine import RuleEngine
from app.engine.strategy_factory import StrategyFactory
from app.exceptions.custom_exception import BadRequestException, NotFoundException
from app.repositories.customer_repository import CustomerRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.promotion_repository import PromotionRepository
from app.schemas.bill import AppliedDiscountLine, BillResponse
from app.schemas.cart import CartCalculateRequest
from app.strategies.base_strategy import CartContext, CartLine, DiscountResult


class PricingEngine:
    """Computes the final payable amount for a cart, discounts included."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.customer_repo = CustomerRepository(db)
        self.product_repo = ProductRepository(db)
        self.promotion_repo = PromotionRepository(db)
        self.rule_engine = RuleEngine()

    def calculate(self, request: CartCalculateRequest) -> BillResponse:
        """Price a cart described by ``request``.

        Args:
            request: The customer, product lines, and optional coupon
                code to price.

        Returns:
            BillResponse: subtotal, applied discounts, total discount,
            and final amount.

        Raises:
            NotFoundException: If the customer or any referenced
                product does not exist.
            BadRequestException: If a cart line has a non-positive
                quantity or references a non-positive-priced product.
        """

        cart_context = self._build_cart_context(request)
        results = self._evaluate_active_promotions(cart_context)
        outcome = self.rule_engine.resolve(results)

        final_amount = round(max(cart_context.subtotal - outcome.total_discount, 0.0), 2)

        applied_lines = [
            AppliedDiscountLine(
                discount_id=r.discount.id,
                name=r.discount.name,
                type=r.discount.type.value
                if hasattr(r.discount.type, "value")
                else str(r.discount.type),
                amount=r.amount,
            )
            for r in outcome.selected
        ]

        return BillResponse(
            customer_id=cart_context.customer.id,
            subtotal=round(cart_context.subtotal, 2),
            applied_discounts=applied_lines,
            total_discount=outcome.total_discount,
            final_amount=final_amount,
        )

    def _build_cart_context(self, request: CartCalculateRequest) -> CartContext:
        """Resolve the customer/products for ``request`` into a ``CartContext``.

        Raises:
            NotFoundException: Customer or product does not exist.
            BadRequestException: Invalid quantity or non-positive price.
        """

        customer = self.customer_repo.get_by_id(request.customer_id)
        if customer is None:
            raise NotFoundException(f"Customer with id {request.customer_id} not found.")

        lines: list[CartLine] = []
        subtotal = 0.0

        for item in request.items:
            if item.quantity <= 0:
                raise BadRequestException("Cart item quantity must be greater than zero.")

            product = self.product_repo.get_by_id(item.product_id)
            if product is None:
                raise NotFoundException(f"Product with id {item.product_id} not found.")

            if product.price <= 0:
                raise BadRequestException(
                    f"Product '{product.name}' has an invalid non-positive price."
                )

            line_total = round(product.price * item.quantity, 2)
            subtotal += line_total
            lines.append(CartLine(product=product, quantity=item.quantity, line_total=line_total))

        return CartContext(
            customer=customer,
            lines=lines,
            subtotal=round(subtotal, 2),
            coupon_code=request.coupon_code,
        )

    def _evaluate_active_promotions(self, cart: CartContext) -> list[DiscountResult]:
        """Evaluate every active, in-window, active-discount promotion.

        Args:
            cart: The cart context to evaluate each strategy against.

        Returns:
            list[DiscountResult]: One result per eligible promotion
            (both applied and not-applied results are included; the
            ``RuleEngine`` is responsible for filtering).
        """

        promotions = self.promotion_repo.list_active_within_window()
        results: list[DiscountResult] = []

        for promotion in promotions:
            discount = promotion.discount
            if discount is None or not discount.active:
                # Ignore promotions whose underlying discount rule has
                # been deactivated, even if the promotion window
                # itself is still open.
                continue

            strategy = StrategyFactory.create(discount)
            results.append(strategy.calculate_discount(cart))

        return results
