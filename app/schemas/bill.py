"""Pydantic schemas describing the output of the Pricing Engine."""

from __future__ import annotations

from pydantic import BaseModel, Field


class AppliedDiscountLine(BaseModel):
    """A single discount that was applied to the cart.

    Attributes:
        discount_id: Identifier of the ``Discount`` that was applied.
        name: Human-readable discount name.
        type: The discount type (as a string, e.g. "PERCENTAGE").
        amount: The monetary amount deducted by this discount.
    """

    discount_id: int
    name: str
    type: str
    amount: float = Field(..., ge=0)


class BillResponse(BaseModel):
    """Final priced result returned by ``POST /cart/calculate``.

    Attributes:
        customer_id: The customer the bill was calculated for.
        subtotal: Sum of (unit price * quantity) across all cart items,
            before any discounts.
        applied_discounts: Ordered list of discounts that were applied.
        total_discount: Sum of all ``applied_discounts[*].amount``.
        final_amount: ``subtotal - total_discount``, floored at 0.
    """

    customer_id: int
    subtotal: float
    applied_discounts: list[AppliedDiscountLine]
    total_discount: float
    final_amount: float
