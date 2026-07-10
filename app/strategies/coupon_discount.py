"""Coupon-code-gated percentage discount strategy."""

from __future__ import annotations

from app.strategies.base_strategy import CartContext, DiscountResult, DiscountStrategy


class CouponDiscountStrategy(DiscountStrategy):
    """Applies a percentage discount only when a matching coupon code is supplied.

    Eligibility: ``cart.coupon_code`` must exactly match (case-insensitive)
    ``discount.coupon_code``, and the cart subtotal must meet
    ``discount.minimum_purchase``.

    Amount: ``discount.value`` percent of the cart subtotal.
    """

    def calculate_discount(self, cart: CartContext) -> DiscountResult:
        if not self._meets_minimum_purchase(cart):
            return self._not_applied()

        expected_code = self.discount.coupon_code
        if not expected_code:
            return self._not_applied()

        supplied_code = cart.coupon_code
        if not supplied_code or supplied_code.strip().upper() != expected_code.strip().upper():
            return self._not_applied()

        amount = round(cart.subtotal * (self.discount.value / 100.0), 2)
        return DiscountResult(discount=self.discount, amount=amount, applied=True)
