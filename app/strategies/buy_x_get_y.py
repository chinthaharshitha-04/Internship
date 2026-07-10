"""'Buy X, Get Y Free' discount strategy."""

from __future__ import annotations

from app.strategies.base_strategy import CartContext, DiscountResult, DiscountStrategy


class BuyXGetYStrategy(DiscountStrategy):
    """Gives free units for every ``buy_quantity`` units purchased.

    Eligibility: the cart must contain at least ``discount.buy_quantity``
    total units of *some* product line, and the cart subtotal must meet
    ``discount.minimum_purchase`` (typically ``0`` for this type).

    Amount: for each cart line, the number of complete
    "buy_quantity + get_quantity" groups is computed. Within each
    complete group, ``get_quantity`` units are free, priced at that
    line's unit price. The cheapest complete groups are effectively
    what get discounted since we always look at the line's own price,
    consistent with typical BOGO-style promotions being scoped per
    product.

    This models the classic "Buy 2 Get 1 Free" pattern: if
    ``buy_quantity=2`` and ``get_quantity=1``, then for every 3 units
    of a qualifying product, 1 is free.
    """

    def calculate_discount(self, cart: CartContext) -> DiscountResult:
        if not self._meets_minimum_purchase(cart):
            return self._not_applied()

        buy_qty = self.discount.buy_quantity or 0
        get_qty = self.discount.get_quantity or 0

        if buy_qty <= 0 or get_qty <= 0:
            return self._not_applied()

        group_size = buy_qty + get_qty
        total_discount = 0.0
        any_line_qualified = False

        for line in cart.lines:
            if line.quantity < group_size:
                continue

            unit_price = line.product.price
            complete_groups = line.quantity // group_size
            free_units = complete_groups * get_qty

            if free_units > 0:
                any_line_qualified = True
                total_discount += free_units * unit_price

        if not any_line_qualified:
            return self._not_applied()

        return DiscountResult(
            discount=self.discount, amount=round(total_discount, 2), applied=True
        )
