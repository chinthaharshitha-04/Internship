"""Strategy Pattern contract for discount calculation.

Every concrete discount type (percentage, flat, buy-X-get-Y, etc.)
implements ``DiscountStrategy``. The ``PricingEngine`` (see
``app.engine.pricing_engine``) never needs to know *how* a particular
discount computes its value -- it only calls ``calculate_discount``
polymorphically, which is the essence of the Open/Closed Principle:
new discount types can be added by writing a new strategy class
without modifying the engine itself.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from app.models.customer import Customer
from app.models.discount import Discount
from app.models.product import Product


@dataclass(frozen=True)
class CartLine:
    """A single priced line within a cart, decoupled from the ORM.

    Using a plain dataclass (rather than passing SQLAlchemy models
    directly into strategies) keeps the Strategy layer independent of
    persistence concerns and makes strategies trivial to unit test
    with plain Python objects.

    Attributes:
        product: The product being purchased.
        quantity: Number of units of the product.
        line_total: ``product.price * quantity``.
    """

    product: Product
    quantity: int
    line_total: float


@dataclass(frozen=True)
class CartContext:
    """All information a ``DiscountStrategy`` needs to evaluate itself.

    Attributes:
        customer: The customer the cart belongs to.
        lines: The priced cart lines.
        subtotal: Sum of all ``lines[*].line_total``.
        coupon_code: Coupon code supplied with the request, if any.
    """

    customer: Customer
    lines: list[CartLine] = field(default_factory=list)
    subtotal: float = 0.0
    coupon_code: str | None = None


@dataclass(frozen=True)
class DiscountResult:
    """The outcome of applying a single discount to a cart.

    Attributes:
        discount: The ``Discount`` that was evaluated.
        amount: The monetary amount to deduct. ``0.0`` means the
            discount was evaluated but did not qualify.
        applied: Whether the discount actually qualifies for this cart.
    """

    discount: Discount
    amount: float
    applied: bool


class DiscountStrategy(ABC):
    """Abstract base class every concrete discount strategy must extend.

    Subclasses encapsulate the eligibility rules and monetary
    calculation for exactly one ``DiscountType``.
    """

    def __init__(self, discount: Discount) -> None:
        self.discount = discount

    @abstractmethod
    def calculate_discount(self, cart: CartContext) -> DiscountResult:
        """Evaluate this discount against the given cart.

        Args:
            cart: The cart context to evaluate eligibility and
                compute the discount amount against.

        Returns:
            DiscountResult: The computed discount outcome. Strategies
            should never raise for "not eligible" -- they should
            return a ``DiscountResult`` with ``applied=False`` and
            ``amount=0.0`` instead, so the engine can uniformly
            process results for every promotion it evaluates.
        """

        raise NotImplementedError

    def _meets_minimum_purchase(self, cart: CartContext) -> bool:
        """Shared helper: check the cart subtotal meets the discount's minimum.

        Args:
            cart: The cart context being evaluated.

        Returns:
            bool: True if the cart's subtotal is at least the
            discount's configured ``minimum_purchase``.
        """

        return cart.subtotal >= self.discount.minimum_purchase

    def _not_applied(self) -> DiscountResult:
        """Convenience factory for a "did not qualify" result."""

        return DiscountResult(discount=self.discount, amount=0.0, applied=False)
