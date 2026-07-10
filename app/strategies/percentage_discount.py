"""Percentage-off-entire-cart discount strategy."""

from __future__ import annotations

from app.strategies.base_strategy import CartContext, DiscountResult, DiscountStrategy


class PercentageDiscountStrategy(DiscountStrategy):
    """Applies a percentage discount to the entire cart subtotal.

    Eligibility: the cart subtotal must meet ``discount.minimum_purchase``.
    Amount: ``subtotal * (discount.value / 100)``.
    """

    def calculate_discount(self, cart: CartContext) -> DiscountResult:
        if not self._meets_minimum_purchase(cart):
            return self._not_applied()

        amount = round(cart.subtotal * (self.discount.value / 100.0), 2)
        return DiscountResult(discount=self.discount, amount=amount, applied=True)
