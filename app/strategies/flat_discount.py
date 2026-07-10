"""Flat (fixed-amount-off) discount strategy."""

from __future__ import annotations

from app.strategies.base_strategy import CartContext, DiscountResult, DiscountStrategy


class FlatDiscountStrategy(DiscountStrategy):
    """Deducts a fixed monetary amount from the cart subtotal.

    Eligibility: the cart subtotal must meet ``discount.minimum_purchase``.
    Amount: ``discount.value``, capped so it never exceeds the subtotal
    (a flat discount should never make the final amount negative).
    """

    def calculate_discount(self, cart: CartContext) -> DiscountResult:
        if not self._meets_minimum_purchase(cart):
            return self._not_applied()

        amount = round(min(self.discount.value, cart.subtotal), 2)
        return DiscountResult(discount=self.discount, amount=amount, applied=True)
