"""Pydantic schemas for Cart / CartItem request payloads."""

from __future__ import annotations

from pydantic import BaseModel, Field


class CartItemInput(BaseModel):
    """A single product line supplied in a price-calculation request."""

    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0, description="Quantity must be greater than zero")


class CartCalculateRequest(BaseModel):
    """Request payload for ``POST /cart/calculate``.

    Attributes:
        customer_id: The customer for whom the cart is being priced.
            Used to evaluate tier-based discounts.
        items: The product lines in the cart.
        coupon_code: Optional coupon code the customer wants to redeem.
    """

    customer_id: int = Field(..., gt=0)
    items: list[CartItemInput] = Field(..., min_length=1)
    coupon_code: str | None = Field(default=None, max_length=50)
