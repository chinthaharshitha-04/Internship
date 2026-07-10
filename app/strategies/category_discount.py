"""Category-scoped percentage discount strategy."""

from __future__ import annotations

from app.strategies.base_strategy import CartContext, DiscountResult, DiscountStrategy


class CategoryDiscountStrategy(DiscountStrategy):
    """Applies a percentage discount only to lines in a given category.

    Eligibility: the cart must contain at least one product whose
    ``category`` matches ``discount.applicable_category``, and the
    *overall* cart subtotal must meet ``discount.minimum_purchase``.

    Amount: ``discount.value`` percent of the summed line totals for
    matching-category products only -- non-matching lines are
    untouched.
    """

    def calculate_discount(self, cart: CartContext) -> DiscountResult:
        if not self._meets_minimum_purchase(cart):
            return self._not_applied()

        category = self.discount.applicable_category
        if not category:
            return self._not_applied()

        matching_total = sum(
            line.line_total for line in cart.lines if line.product.category == category
        )

        if matching_total <= 0:
            return self._not_applied()

        amount = round(matching_total * (self.discount.value / 100.0), 2)
        return DiscountResult(discount=self.discount, amount=amount, applied=True)
