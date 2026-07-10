"""Customer-loyalty-tier percentage discount strategy."""

from __future__ import annotations

from app.core.constants import TIER_RANK
from app.strategies.base_strategy import CartContext, DiscountResult, DiscountStrategy


class CustomerTierDiscountStrategy(DiscountStrategy):
    """Applies a percentage discount based on the customer's loyalty tier.

    Eligibility: the customer's tier must be at least as high as
    ``discount.required_tier`` (Platinum > Gold > Silver), and the
    cart subtotal must meet ``discount.minimum_purchase``.

    Amount: ``discount.value`` percent of the cart subtotal.
    """

    def calculate_discount(self, cart: CartContext) -> DiscountResult:
        if not self._meets_minimum_purchase(cart):
            return self._not_applied()

        required_tier = self.discount.required_tier
        if required_tier is None:
            return self._not_applied()

        customer_rank = TIER_RANK.get(cart.customer.tier, 0)
        required_rank = TIER_RANK.get(required_tier, 0)

        if customer_rank < required_rank:
            return self._not_applied()

        amount = round(cart.subtotal * (self.discount.value / 100.0), 2)
        return DiscountResult(discount=self.discount, amount=amount, applied=True)
