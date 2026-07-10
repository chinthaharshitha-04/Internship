"""Factory Pattern: maps a ``DiscountType`` to its ``DiscountStrategy``.

Keeping this mapping in one place means adding a new discount type is
a two-step change (write the strategy class, register it here) rather
than a search-and-replace across the codebase -- another expression of
the Open/Closed Principle working alongside the Strategy pattern.
"""

from __future__ import annotations

from app.core.constants import DiscountType
from app.exceptions.custom_exception import BadRequestException
from app.models.discount import Discount
from app.strategies.base_strategy import DiscountStrategy
from app.strategies.buy_x_get_y import BuyXGetYStrategy
from app.strategies.category_discount import CategoryDiscountStrategy
from app.strategies.coupon_discount import CouponDiscountStrategy
from app.strategies.customer_tier_discount import CustomerTierDiscountStrategy
from app.strategies.flat_discount import FlatDiscountStrategy
from app.strategies.percentage_discount import PercentageDiscountStrategy

_STRATEGY_REGISTRY: dict[DiscountType, type[DiscountStrategy]] = {
    DiscountType.PERCENTAGE: PercentageDiscountStrategy,
    DiscountType.FLAT: FlatDiscountStrategy,
    DiscountType.BUY_X_GET_Y: BuyXGetYStrategy,
    DiscountType.CATEGORY: CategoryDiscountStrategy,
    DiscountType.CUSTOMER_TIER: CustomerTierDiscountStrategy,
    DiscountType.COUPON: CouponDiscountStrategy,
}


class StrategyFactory:
    """Creates the correct ``DiscountStrategy`` instance for a ``Discount``."""

    @staticmethod
    def create(discount: Discount) -> DiscountStrategy:
        """Instantiate the strategy matching ``discount.type``.

        Args:
            discount: The discount row whose ``type`` selects the
                strategy implementation.

        Returns:
            DiscountStrategy: A ready-to-use strategy bound to
            ``discount``.

        Raises:
            BadRequestException: If ``discount.type`` has no
                registered strategy implementation.
        """

        strategy_cls = _STRATEGY_REGISTRY.get(discount.type)
        if strategy_cls is None:
            raise BadRequestException(
                f"No discount strategy registered for type '{discount.type}'."
            )
        return strategy_cls(discount)
